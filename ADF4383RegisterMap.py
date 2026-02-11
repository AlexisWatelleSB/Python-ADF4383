from enum import Enum


class ADF4383RegisterMap(Enum):
    # Types
    # - 0 = int
    # - 1 = Decimal
    # - 2 = Long Int
    # - 3 = Bool
    # - 4 = Write bit
    # - 5 = Write Byte
    N_INT = ["N_INT",2]

    SOFT_RESET = ["SOFT_RESET",0]
    FRAC1WORD = ["FRAC1WORD",2]
    FRAC2WORD = ["FRAC2WORD",2]
    M_VCO_CORE = ["M_VCO_CORE",0]
    M_VCO_BAND = ["M_VCO_BAND",2]
    M_VCO_BIAS = ["M_VCO_BIAS",0]
    R_DIV = ["R_DIV",5]
    EN_AUTOCAL = ["EN_AUTOCAL",0]

    # Power Down [reg 24]
    PD_RFOUT2 = ["PD_RFOUT2", 0]
    PD_RFOUT1 = ["PD_RFOUT1", 0]
    PD_PFDCP = ["PD_PFDCP", 0]
    PD_LD = ["PD_LD", 0]
    PD_VCO = ["PD_VCO", 0]
    PD_NDIV = ["PD_NDIV", 0]
    PD_RDIV = ["PD_RDIV", 0]
    PD_ALL = ["PD_ALL", 0]

    EN_LUT_CAL = ["54",4]
    EN_LUT_GEN = ["EN_LUT_GEN",3]
    LUT_SCALE = ["LUT_SCALE",0]
    REF_SEL = ["REF_SEL",0] # Selection mode oscillateur, 0 pour DMA
    EN_RDBLR = ["EN_RDBLR",0] # Doubleur d'entrée x2
    RFOUT_DIV = ["RFOUT_DIV",0] # Diviseur de retour, 2 = /4

    O_VCO_CORE = ["O_VCO_CORE",0]
    O_VCO_BAND = ["O_VCO_BAND",0]
    O_VCO_BIAS = ["O_VCO_BIAS",3]

    VPTAT_CALGEN = ["REG44_RSV0",5]
    VCTAT_CALGEN = ["REG45_RSV0",5]
    INT_MODE = ["INT_MODE",0]

    FSM_BUSY = ["FSM_BUSY",0]
    LUT_BUSY = ["LUT_BUSY",3]
    LUT_BAND_N = ["LUT_BAND_N",2]

    CAL_VTUNE_TO = ["CAL_VTUNE_TO",2]
    PD_CALGEN = ["REG2A_RSV0",3]

    M_LUT_CORE = ["M_LUT_CORE",3]
    M_LUT_BAND = ["M_LUT_BAND",2]
    M_LUT_N = ["M_LUT_N",2]

    LUT_WR_ADDR = ["LUT_WR_ADDR",5]
    O_VCO_LUT = ["O_VCO_LUT",3]

    VCO_BAND = ["VCO_BAND",2]
