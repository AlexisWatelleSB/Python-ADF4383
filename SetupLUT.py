# Generated code compatible with Python 2.7+

## Copyright (c) 2026 by Analog Devices, Inc.  All rights reserved.  This software is proprietary to Analog Devices, Inc. and its licensors.
## This software is provided on an 'as is' basis without any representations, warranties, guarantees or liability of any kind.
## Use of the software is subject to the terms and conditions of the Clear BSD License ( https://spdx.org/licenses/BSD-3-Clause-Clear.html ).

# Requirements:
#  - pythonnet


import sys

#from Old.ADF4383 import ADF4383 as ADF4383
from ADF4383Registers import ADF4383Registers as ADF4383

sys.path.append(r'C:\Program Files (x86)\Analog Devices\ACE\Client')

# noinspection SpellCheckingInspection
import clr  # noqa
# noinspection SpellCheckingInspection
clr.AddReference('AnalogDevices.Csa.Remoting.Clients')
clr.AddReference('AnalogDevices.Csa.Remoting.Contracts')

# noinspection PyUnresolvedReferences,SpellCheckingInspection
from AnalogDevices.Csa.Remoting.Clients import ClientManager  #noqa


def main():
    manager = ClientManager.Create()
    client = manager.CreateRequestClient("localhost:2357")
    client.ContextPath = r"\System\Subsystem_1\ADF4382 Board\ADF4383"
    execute_macro(client)
    # client.CloseSession()


# noinspection SpellCheckingInspection
def execute_macro(client):
    print("Début de la macro")
    ADF = ADF4383(client)
    print("ADF4383 initialisé")
    ADF.setupInternLUT()
    #ADF.overwriteLUT()
    ADF.plotInternalLUT()
    ADF.printInternalClock()
    ADF.plotVCOBANDS(20,30)
    print("Fin du scan des VCOBANDS")
    input("Enter de continue")
    ADF.setFrequencyN(3000)
    input("Enter de continue")
    ADF.setFrequencyN(2600)
    input("Enter de continue")
    ADF.setFrequencyN(2800)
    print("Fin de la scéance")


if __name__ == "__main__":
    main()