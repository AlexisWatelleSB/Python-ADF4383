import math
import logging
import time

import matplotlib.pyplot as plt
import numpy as np

from ADF4383RegisterMap import ADF4383RegisterMap as RegMap


class ADF4383():
    def __init__(self,client):
        self.logger  = logging.getLogger(__name__)
        logging.basicConfig(filename='Log.txt', level=logging.INFO)
        self.logger.info(" --- [ Init de la classe ADF4383 ] ---")
        self.client = client
        self.powerDownAll(0) # Activer tous les blocs internes de la PLL
        self.writeParameter(RegMap.EN_RDBLR,0) # Desactivier doubleur
        # self.client.SetIntParameter("virtual-parameter-rfout-div-0", "2", "-1")
        self.writeParameter(RegMap.RFOUT_DIV,2) # Mettre /4 sur retour
        self.pushParameters()
        self.writeParameter(RegMap.REF_SEL,0) # Prendre mode DMA
        self.writeParameter(RegMap.M_VCO_CORE,1) # prendre le core avec plus petit fréquence
        self.writeParameter(RegMap.R_DIV,1) # Mettre diviseur d'entrée à 1
        # self.client.WriteRegister("32", "129")  # Met EN_AUTOCAL à ON

        self.pushParameters()

    def powerDownAll(self,value = 1):
        self.writeParameter(RegMap.PD_ALL,value)
        self.writeParameter(RegMap.PD_RFOUT1,value)
        self.writeParameter(RegMap.PD_RFOUT2,1)
        self.writeParameter(RegMap.PD_LD,value)
        self.writeParameter(RegMap.PD_VCO, value)
        self.writeParameter(RegMap.PD_NDIV, value)
        self.writeParameter(RegMap.PD_RDIV, value)
        self.writeParameter(RegMap.PD_PFDCP, value)

    def pushParameters(self):
        self.client.Run("@ApplySettings")

    def overwriteLUT(self):
        N = np.arange(20,27,1)
        freqs = self.N2freq(N)
        bands = -0.42 * freqs + 1467.4
        for i in range(len(N)):
            self.writeParameter(RegMap.M_LUT_CORE,1)
            self.writeParameter(RegMap.M_LUT_BAND,np.round(bands[i],0))
            self.writeParameter(RegMap.M_LUT_N,np.round(N[i],0))
            self.pushParameters()
            self.writeParameter(RegMap.LUT_WR_ADDR,i)
            self.pushParameters()
            self.writeParameter(RegMap.O_VCO_LUT,1)
            self.pushParameters()
            time.sleep(0.05)

    def writeParameter(self,param:RegMap,valeur):
        self.logger.info(f"Ecriture de \t{valeur}\t\t dans {param.name} ")
        if(param.value[1] == 5):
            self.client.SetByteParameter(param.value[0], int(valeur))
        elif param.value[1] == 4:
            if valeur:
                self.client.SetRegisterBit(param.value[0], "1", "True", "-1")
            else:
                self.client.SetRegisterBit(param.value[0], "0", "False", "-1")
        elif param.value[1] == 3:
            if valeur:
                self.client.SetBoolParameter(param.value[0], "True","-1")
            else:
                self.client.SetBoolParameter(param.value[0], "False","-1")

        elif param.value[1] == 2:
            self.client.SetBigIntParameter(param.value[0], int(valeur))
        elif param.value[1] == 1:
            self.client.SetDecimalParameter(param.value[0], str(valeur))
        else:
            self.client.SetIntParameter(param.value[0],str(int(valeur)),"-1")

    def readParameter(self,param:RegMap):
        self.client.Run("@ReadSettings")
        if (param.value[1] == 5):
            valeur = self.client.GetByteParameter(param.value[0])
        elif (param.value[1] == 3):
            valeur = self.client.GetBoolParameter(param.value[0])
        elif (param.value[1] == 2):
            valeur = self.client.GetBigIntParameter(param.value[0])
        elif (param.value[1] == 1):
            valeur = self.client.GetDecimalParameter(param.value[0])
        else:
            valeur = self.client.GetIntParameter(param.value[0])
        self.logger.info(f"Lecture de \t{valeur}\t\t dans {param.name} ")
        return int(valeur)

    def freq2N(self,freqMHz):
        Fvco = freqMHz * 4
        N = Fvco / (125 * 4)
        return N

    def N2freq(self,N):
        Fvco = N * 125 * 4
        freqMHz = Fvco / 4
        return freqMHz

    def setFrequencyN(self,freqMHz):
        N = self.freq2N(freqMHz)
        Nint = math.floor(N)
        NFrac = math.floor(33554432 * (N - Nint))

        self.writeFrac1Word(NFrac)
        self.client.WriteRegister("16", Nint)  # Nint


    def setAutoCalibration(self,value):
        self.writeParameter(RegMap.EN_AUTOCAL,value)

    def setManualFrequency(self,freqMHz):
        band = -0.42*freqMHz+1467.4
        self.writeParameter(RegMap.O_VCO_CORE,1)
        self.writeParameter(RegMap.O_VCO_BAND,1)
        self.setFrequencyN(freqMHz)
        self.writeParameter(RegMap.M_VCO_CORE,1)
        self.writeParameter(RegMap.M_VCO_BAND,int(band))

    def removeManualCalibration(self):
        self.writeParameter(RegMap.O_VCO_CORE, 0)
        self.writeParameter(RegMap.O_VCO_BAND, 0)

    def writeFrac1Word(self, frac_value: int):
        """
        Ecrit directement FRAC1WORD[24:0] via WriteRegister()
        Compatible ACE (Read = hex string, Write = decimal string)
        """

        if frac_value < 0 or frac_value > (2 ** 25 - 1):
            raise ValueError("FRAC1WORD doit être entre 0 et 2^25 - 1")

        # ----------------------------
        # Découpage des 25 bits
        # ----------------------------
        reg12 = frac_value & 0xFF
        reg13 = (frac_value >> 8) & 0xFF
        reg14 = (frac_value >> 16) & 0xFF
        bit24 = (frac_value >> 24) & 0x01

        # ----------------------------
        # Conversion adresses HEX -> DECIMAL
        # ----------------------------
        addr12 = str(int("0x12", 16))  # 18
        addr13 = str(int("0x13", 16))  # 19
        addr14 = str(int("0x14", 16))  # 20
        addr15 = str(int("0x15", 16))  # 21

        # ----------------------------
        # Lecture REG0015 (retourne hex string)
        # ----------------------------
        current_reg15 = int(
            self.client.ReadRegister(addr15).strip(),
            16
        )

        # ----------------------------
        # Modification uniquement du bit FRAC1WORD[24]
        # (supposé être bit0 — vérifier datasheet)
        # ----------------------------
        new_reg15 = (current_reg15 & 0xFE) | bit24

        # ----------------------------
        # Ecriture registres (decimal string)
        # ----------------------------
        self.client.WriteRegister(addr12, str(reg12))
        self.client.WriteRegister(addr13, str(reg13))
        self.client.WriteRegister(addr14, str(reg14))
        self.client.WriteRegister(addr15, str(new_reg15))

    def setNandDivider(self, Nint):
        self.client.WriteRegister("16", Nint) # Nint
        self.client.WriteRegister("17", "64") # Divider at /4



    def setupInternLUT(self):
        self.writeParameter(RegMap.VCTAT_CALGEN,21)
        self.writeParameter(RegMap.VPTAT_CALGEN,7)
        self.setAutoCalibration(True)
        self.client.WriteRegister("32", "130")
        self.writeParameter(RegMap.EN_LUT_CAL, 0)
        self.writeParameter(RegMap.INT_MODE, 1)
        self.setNandDivider(21)
        self.pushParameters()

        self.writeParameter(RegMap.EN_LUT_GEN, 1)
        self.pushParameters()

        print("Après LUT_GEN:", self.readParameter(RegMap.RFOUT_DIV))
        print("Après LUT_GEN (N_int):", self.readParameter(RegMap.N_INT))

        # while self.readParameter(RegMap.LUT_BUSY) == "True\n":
        #     print("Attente de la génération LUT")
        attente = 1
        counter = 0
        while int(self.readParameter(RegMap.FSM_BUSY)) == 1:
            time.sleep(0.01)
            counter = counter + 1
            print(f"Attente de FSM_BUSY : {counter}")

        self.writeParameter(RegMap.LUT_SCALE,2)

        self.pushParameters()
        self.client.WriteRegister("32", "129")
        self.writeParameter(RegMap.CAL_VTUNE_TO, 0)
        self.writeParameter(RegMap.INT_MODE, 0)
        self.pushParameters()
        self.client.WriteRegister("54", "129") # disable EN_LUT_GEN, enable EN_LUT_CAL
        # self.client.WriteRegister("32", "1") # Met le EN_AUTOCAL à off
        #.client.WriteRegister("44", "164") # Met les LDWIN et LD coutn
        self.client.WriteRegister("44", 0b10000100)


    def writeBigIntByName(self,name,value):
        self.client.SetBigIntParameter(name,value)

    def writeBoolByName(self, name, value):
        if(value):
            self.client.SetBigIntParameter(name, "True","-1")
        else:
            self.client.SetBigIntParameter(name, "False", "-1")

    def getVCOBAND(self):
        return self.readParameter(RegMap.VCO_BAND)

    def plotVCOBANDS(self,NStart,NStop):
        N = np.arange(NStart,NStop,1)
        VCO_BANDS = np.array([])
        for n_int in N:
            self.setNandDivider(str(n_int))
            VCO_BANDS = np.append(VCO_BANDS,self.getVCOBAND())

        plt.figure()
        plt.plot(N,VCO_BANDS,marker='o')
        plt.title("Mapping du VCO_BANDS vs N")
        plt.xlabel("N")
        plt.ylabel("VCO_BANDS")
        plt.show()


    def printInternalClock(self):
        print(f"Doubleur : {self.readParameter(RegMap.EN_RDBLR)}")
        print(f"Diviseur : {self.readParameter(RegMap.R_DIV)}")
        print(f"Nint \t: {self.readParameter(RegMap.N_INT)}")
        print(f"VCO_BAND : {self.readParameter(RegMap.VCO_BAND)}")

    def readBigIntByName(self,name):
        self.client.Run("@ReadSettings")
        valeur = self.client.GetBigIntParameter(name)
        return valeur

    def readInternalLUT(self, count: int = 32):
        self.client.Run("@ReadSettings")
        vals = []
        vals_N = []
        for i in range(count):
            name = f"LUT_BAND_{i}"
            name_N = f"LUT_N_{i}"
            try:
                vals.append(self.readBigIntByName(name))  # helper direct par nom
                vals_N.append(self.readBigIntByName(name_N))  # helper direct par nom
            except Exception as e:
                self.logger.warning(f"Lecture {name} échouée: {e}")
                break
        return np.array(vals, dtype=int),np.array(vals_N, dtype=int)

    def plotInternalLUT(self, count: int = 32, show=True, savepath=None):
        bands,LUT_N = self.readInternalLUT(count)
        if bands.size == 0:
            print("Aucune donnée LUT lue.")
            return
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.plot(np.arange(bands.size), bands, marker='o')
        ax.set_title("ADF4383 - Valeurs LUT internes")
        ax.set_xlabel("Index de bande")
        ax.set_ylabel("LUT_BAND")
        ax.grid(True, ls='--', alpha=0.4)

        fig, ax = plt.subplots(figsize=(7, 4))
        ax.plot(np.arange(LUT_N.size), LUT_N, marker='o')
        ax.set_title("ADF4383 - Valeurs LUT internes N")
        ax.set_xlabel("Index de bande")
        ax.set_ylabel("LUT_N")
        ax.grid(True, ls='--', alpha=0.4)

        fig, ax = plt.subplots(figsize=(7, 4))
        ax.plot(self.N2freq(LUT_N), bands, marker='o')
        ax.set_title("ADF4383 - Valeurs LUT internes N")
        ax.set_xlabel("Fréquence (MHz)")
        ax.set_ylabel("VCO_BAND")
        ax.grid(True, ls='--', alpha=0.4)

        if savepath:
            fig.tight_layout();
            fig.savefig(savepath, dpi=300)
        if show:
            plt.show()
        else:
            plt.close(fig)


