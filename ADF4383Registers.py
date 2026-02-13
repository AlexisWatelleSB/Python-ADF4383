import math
import time

import matplotlib.pyplot as plt
import numpy as np

from ADF4383RegisterMap import ADF4383RegisterMap as RegMap

class ADF4383Registers:
    def __init__(self,client):
        self.client = client
        # Configuration générale
        self.client.WriteRegister(0x0, 0x18) # Clear les resets au démarage
        self.client.WriteRegister(0x1E, 0x29) # Met les paramètres de bleed de la chip
        self.client.WriteRegister(0x2D, 0x0F0) # Active les clock internes
        self.client.WriteRegister(0x31, 0x09) # Active la clock de l'ADC
        self.client.WriteRegister(0x29, 0x09) # Power output amplitude
        self.client.WriteRegister(0x34, 0x36) # Input delay to CLK path
        self.client.WriteRegister(0x3F, 0x082) # Enable ADC
        self.client.WriteRegister(0x24, 0x0) # Clock control
        self.client.WriteRegister(0x3B, 0x0) # Delay control double buffer

        # Config de la charge pump
        self.client.WriteRegister(0x15, 0x082)
        self.client.WriteRegister(0x1D, 0x20)
        self.client.WriteRegister(0x1E, 0x29)
        self.client.WriteRegister(0x1F, 0x1F)

        # Écriture des bias table
        for reg in np.arange(0x100, 0x112, 1):
            self.client.WriteRegister(str(reg),0x3F)
        self.client.WriteRegister(0x109,0x25)
        self.client.WriteRegister(0x10A, 0x25)

        # Configuration du chemin d'entrée (clk)
        self.client.WriteRegister(0x2F, 0x3F)
        self.client.WriteRegister(0x30, 0x0F)


        # Mettre les bons power down
        self.client.WriteRegister(0x2A, 0x30)
        self.client.WriteRegister(0x2B, 0x1)

    def setupInternLUT(self):
        self.client.WriteRegister(0x20, 0x082) # Diviseur d'entrée
        self.client.WriteRegister(0x10, 0x15) # N_int
        self.client.WriteRegister(0x11, 0x40) # N_int
        self.client.WriteRegister(0x15, 0x086) # Désactiver mode fractionnaire
        self.client.WriteRegister(0x1F, 0x0F) # Paramètres de bleed
        self.client.WriteRegister(0x2C, 0x28) # Lock detect window
        self.client.WriteRegister(0x36, 0x080) # Désactive la calibration via LUT

        self.client.WriteRegister(0x37, 0x5C) # coefficients de température
        self.client.WriteRegister(0x38, 0x78) # coefficients de température
        self.client.WriteRegister(0x3A, 0x3F) # coefficients de température

        self.client.WriteRegister(0x3E, 0x27) # ADC calib
        self.client.WriteRegister(0x10, 0x2A) # N_INT de départ

        self.client.WriteRegister(0x36, 0x082) # Lancer génération LUT
        self.client.WriteRegister(0x10, 0x2A) # N_int pour lancer la génération
        # Doubler commande de N_INT ?

        time.sleep(2) # Attente fin de calibration
        self.client.WriteRegister(0x20, 0x081) # Mettre R_DIV à 1
        self.client.WriteRegister(0x15, 0x082) # Réactiver mode fractionnel
        self.client.WriteRegister(0x1F, 0x1F) # Bleed current
        self.client.WriteRegister(0x2C, 0x2A) # LDWIN

        # Coefficients de température
        self.client.WriteRegister(0x37, 0x0B8)
        self.client.WriteRegister(0x38, 0x0)
        self.client.WriteRegister(0x3A, 0x7D)

        self.client.WriteRegister(0x3E, 0x4E) # ADC clock
        self.client.WriteRegister(0x10, 0x15) # N_int à 21
        self.client.WriteRegister(0x4F, 0x02) # Mettre LUT scale à 2
        self.client.WriteRegister(0x36, 0x081) # Activer la calibration via LUT
        self.client.WriteRegister(0x2C, 0x084) # LD_WIN parameters

    def freq2N(self, freqMHz):
            Fvco = freqMHz * 4
            N = Fvco / (125 * 4)
            return N

    def N2freq(self, N):
            Fvco = N * 125 * 4
            freqMHz = Fvco / 4
            return freqMHz

    def setFrequencyN(self, freqMHz):
        N = self.freq2N(freqMHz)
        Nint = math.floor(N)
        NFrac = math.floor(33554432 * (N - Nint))

        self.writeFrac1Word(NFrac)
        self.client.WriteRegister("16", Nint)  # Nint

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

        return int(valeur)

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
                print(f"Lecture {name} échouée: {e}")
                break
        return np.array(vals, dtype=int),np.array(vals_N, dtype=int)

    def setNandDivider(self, Nint):
        self.client.WriteRegister("16", Nint) # Nint
        self.client.WriteRegister("17", "64")  # Divider at /4

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