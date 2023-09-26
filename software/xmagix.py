import time
from rich import print
from rich.console import Console
import numpy as np
from ctypes import *
from theapp_errors import *
from theapp_constants import *
from theacquisition_values import *
from theboardoperations import *

console = Console()

class XMagix:
    """Wrapper class to expose handel API functions."""

    def __init__(self, libpath):
        self.systemUp = False
        self._lib = None
        self.libpath = libpath
        self.cdetChan = c_int(0)
        try:
            self._lib = cdll.LoadLibrary(self.libpath)
        except Exception:
            # Return traceback on error
            console.log("[red]Aw naw :disappointed: wrong file/path?[red]")
        else:
            console.log("[green]Library loaded successfully :smile:[/green]")


    def stringToBytes(self, mystring):
        """Converts python string to C/C++ byte stream"""
        return mystring.encode('ascii')

    def CHECK_ERROR(self, message):
        try:
            self.errmessage = ERRORS[self.status]
        except:
            console.log(f"Errorcode {self.status} unknown :rolleyes:")
        else:
            if self.status != 0:
                console.log(f"[dark_orange] :warning: {self.status}, {self.errmessage}")
            else:
                console.log(f"{message}", justify="left")
        self.status = None

    def getAllowedAcquisitionParams(self, verbose=False):
        """Prints a list of allowed acquisition parameters to the console."""

        for key, item in acquisition_values.items():
            if verbose == False:
                console.console.log(f"[bold]{key}[/bold]")
            if verbose == True:
                console.console.log(f"[bold]{key}:[/bold] {item}")
            else:
                console.console.log(f"[dark_orange] :warning: <verbose> expects boolean values.")

    def setLogging(self, level, logpath="/tmp/xmagix.log"):
        """Sets the logging level, logfile output path and filename."""

        self.logpath = logpath
        self.level = level

        self._lib.xiaSetLogLevel(self.level)
        self._lib.xiaSetLogOutput(self.stringToBytes(self.logpath))
        console.log(f"Logfile set to {logpath}")

    def init(self, inifile):
        """Initializes the Handel library and loads in an .ini file. The functionality of this
        routine can be emulated by calling xiaInitHandel() followed by xiaLoadSys-
        tem()("handel_ini", iniFile). Either this routine or xiaInitHandel must be
        called prior to using the other Handel routines.
        """

        self.inifile = inifile
        self.status = self._lib.xiaInit(self.stringToBytes(inifile))
        self.CHECK_ERROR("Loading system...")

    def exit(self, exitmessage="Exiting..."):
        """Disconnects from the hardware and cleans up Handel's internal data structures."""
        
        self.status = self._lib.xiaExit()
        self.CHECK_ERROR(f"{exitmessage}")

    def startSystem(self):
        """Starts the system previously defined via an .ini file."""

        if self.inifile and self.logpath:
            self.status = self._lib.xiaStartSystem()
            self.CHECK_ERROR("Starting system...")
        else:
            console.log("Set <logpath> and specify <inifile> first.")
        
    def boardOperation(self, name, value):
        """Performs product-specific queries and operations.
        
        Parameters:
        ----------
        name : str
            Type of data to pass or return. Reference the product-specific Handel manuals for complete lists by product.
        value : int
            Variable to return the data in, cast into a void *. See the product-specific Handel manuals for the required data type for each name.

        Return Codes
        ----------
        XIA_INVALID_DETCHAN Specified detChan does not exist or is not associated with a known module.
        XIA_BAD_TYPE detChan refers to a detChan set, which is not allowed in this routine.
        XIA_UNKNOWN Internal Handel error. Contact XIA.
        XIA_BAD_CHANNEL Internal Handel error. Contact XIA.
        """

        self.boardOpName = self.stringToBytes(name)
        self.boardOpValue = c_double(value)

        self.status = self._lib.xiaBoardOperation(self.cdetChan, self.boardOpName, self.boardOpValue)
        self.CHECK_ERROR()

    def setAcquisitionValues(self, name, value):
        """
        Translates a high-level acquisition value into the appropriate DSP parameter(s)
        in the hardware. Product-specific Handel manuals list the acquisition values for
        each product.
        """

        if name not in acquisition_values:
            console.log(f"[dark_orange] :warning: Parameter \"{name}\" unknown.")
        else:
            cname = self.stringToBytes(name)
            cvalue = c_double(value)

            self.status = self._lib.xiaSetAcquisitionValues(self.cdetChan, cname, byref(cvalue))
            self.CHECK_ERROR(f"Setting '{name}' to {value}...")

    def getAcquisitionValues(self, name) -> dict:
        """Retrieves the current setting of an acquisition value. This routine returns the same value as xiaSetAcquisitionValues() in the value parameters."""
        cvalue = c_double(0)

        self.acquisitionParams = []
        self.acquisitionValues = []
        if name == "all":
            for key in acquisition_values:
                self.status = self._lib.xiaGetAcquisitionValues(self.cdetChan, self.stringToBytes(key), byref(cvalue))
                self.acquisitionParams.append(key)
                self.acquisitionValues.append(cvalue.value)
            self.acquisitionValuesDict = dict(zip(self.acquisitionParams, self.acquisitionValues))
        else:
            if name in acquisition_values:
                console.log(f"{name}: {self.acquisitionValuesDict[name]}")
                return self.acquisitionValuesDict[name]
            else:
                console.log(f"[dark_orange] :warning: Parameter <name> unknown.")
                pass
                
        return self.acquisitionValuesDict
    
    def getBoardInformation(self):
        """Retrieves Board INformation."""

        binfo = ["PIC Code Variant",
                "PIC Code Major Version",
                "PIC Code Minor Version",
                "DSP Code Variant",
                "DSP Code Major Version",
                "DSP Code Minor Version",
                "DSP Clock Speed",
                "Clock Enable Register",
                "Number of FiPPIs",
                "Gain Mode",
                "Gain (mantissa low byte)",
                "Gain (mantissa high byte)",
                "Gain (exponent)",
                "Nyquist Filter",
                "ADC Speed Grade",
                "FPGA Speed",
                "Analog Power Supply",
                "FiPPI 0 Decimation",
                "FiPPI 0 Version",
                "FiPPI 0 Variant"]
        
        cchararray = (c_char * 26)(0)

        self._lib.xiaBoardOperation(self.cdetChan, self.stringToBytes("get_board_info"), byref(cchararray))
        chararray = np.frombuffer(np.ctypeslib.as_array(cchararray), dtype=np.int8)
        binfo = dict(zip(binfo, chararray.tolist()))
        return binfo

    def setParams(self, params):
        """Setting parameters. Defaults taken from XIAs Programmer Guide"""

        # ACQ_MEM_CONSTANTS[AV_MEM_PARSET] = 0x04
        # ACQ_MEM_CONSTANTS[AV_MEM_GENSET] = 0x08
        cparsetAndGenset = c_short(ACQ_MEM_CONSTANTS["AV_MEM_PARSET"] | ACQ_MEM_CONSTANTS["AV_MEM_GENSET"])
        for key in params:
            if key not in acquisition_values:
                console.log(f"[dark_orange] :warning: Bad key given.")
                return None

        for key, value in params.items():
            self.cvalue = c_double(value)
            console.log(f"Setting {key}: {self.cvalue.value}")
            self.status = self._lib.xiaSetAcquisitionValues(self.cdetChan, self.stringToBytes(key), byref(self.cvalue))
        # Need to call "apply" after setting acquisition values. */
        self.status = self._lib.xiaBoardOperation(self.cdetChan, self.stringToBytes("apply"), byref(cparsetAndGenset))
        self.CHECK_ERROR("Applying changes...")

    def applyParams(self, parset, genset):

        if parset or genset not in ACQ_MEM_CONSTANTS:
            console.log(f"[dark_orange] Xwarning: Bad PARSET/GENSET given.")
            return None
        self.cparsetAndGenset = c_short(ACQ_MEM_CONSTANTS[parset] | ACQ_MEM_CONSTANTS[genset])

        # Need to call "apply" after setting acquisition values. */
        console.log("Applying changes...")
        self.status = self._lib.xiaBoardOperation(self.cdetChan, self.stringToBytes("apply"), byref(self.cparsetAndGenset))
        self.CHECK_ERROR("Applying changes...")

    def startRun(self, clearMca=0):
        self.cclearMca = c_short(clearMca)

        self.status = self._lib.xiaStartRun(self.cdetChan, self.cclearMca)
        self.CHECK_ERROR(f"Run started until stopped by user...")
        self.isRunning = True

    def fixedRealtimeRun(self, realtime, clearMca=True):
        """Start fixed realtime run."""

        if type(realtime) == str:
            realtime = float(realtime)
        clearMca = not clearMca
        self.cclearMca = c_short(clearMca) # 0: DO clear MCA, 1: do NOT clear MCA
        crunActive = c_short(0)
        coutputCountRate = c_double(0)
        ceventsInRun = c_ulong(0)
        cruntime = c_double(0)

        self.status = self.setAcquisitionValues("preset_type", CONSTANTS["XIA_PRESET_FIXED_REAL"])
        self.status = self.setAcquisitionValues("preset_value", realtime)

        self.status = self._lib.xiaStartRun(self.cdetChan, self.cclearMca)
        self.CHECK_ERROR("Starting Run...")

        console.clear()
        with console.status(":satellite: out cps: 0, Events: 0") as status:
            for _ in range(10*int(realtime)):
                self._lib.xiaGetRunData(self.cdetChan, self.stringToBytes("output_count_rate"), byref(coutputCountRate))
                self._lib.xiaGetRunData(self.cdetChan, self.stringToBytes("events_in_run"), byref(ceventsInRun))
                self._lib.xiaGetRunData(self.cdetChan, self.stringToBytes("run_active"), byref(crunActive))
                self._lib.xiaGetRunData(self.cdetChan, self.stringToBytes("runtime"), byref(cruntime))
                status.update(f":satellite: Time: {cruntime.value:.1f}/{realtime:.1f}, out cps: {coutputCountRate.value:.2f}, Events: {ceventsInRun.value}")
                if crunActive.value == 0:
                    break
                time.sleep(.1)
        console.log(f"Done. Run statistics: out cps: {coutputCountRate.value:.2f}, Events: {ceventsInRun.value}")
        self.status = self.setAcquisitionValues("preset_type", CONSTANTS["XIA_PRESET_FIXED_NONE"])
        
    def stopRun(self, stopmessage="Stopped..."):
        """Stops an active run."""

        crunActive = c_short(0)
        self.status = self._lib.xiaGetRunData(self.cdetChan, self.stringToBytes("run_active"), byref(crunActive))

        if self.crunActive.value != 0:
            self.status = self._lib.xiaStopRun(0)
            self.CHECK_ERROR(f"{stopmessage}")
        else:
            console.log(f"No run started. Nothing to do...")

    def pullMcaData(self):
        """Time to read out the MCA"""
        
        nmca = self.getAcquisitionValues(name="number_mca_channels")
        cmca = (c_ulong * int(nmca))()

        self.status = self._lib.xiaGetRunData(self.cdetChan, self.stringToBytes("mca"), byref(cmca))
        self.CHECK_ERROR("Pulling MCA...")

        mca = np.ctypeslib.as_array(cmca)
        return mca
    
    def getNumDetectors(self) -> int:
        """Returns the number of detectors currently defined in the system."""

        self.cnumDet = c_int(0)
        self.status = self._lib.xiaGetNumDetectors(byref(self.cnumDet))
        if self.status == 0:
            self.CHECK_ERROR(f"There are currently {self.cnumDet.value} detectors defined")
        else:
            self.CHECK_ERROR("Could not read get num defined detectors.")

        return self.cnumDet.value
    
    def getNumFirmwareSets(self) -> int:
        """Returns the number of firmware sets defined in the system."""

        self.cnumFwSets = c_int(0)
        self.status = self._lib.xiaGetNumFirmwareSets(byref(self.cnumFwSets))
        if self.status == 0:
            self.CHECK_ERROR(f"There are currently {self.cnumFwSets.value} firmware sets defined")
        else:
            self.CHECK_ERROR("Could not read get num defined firmwares sets.")

        return self.cnumFeSets.value
    
    def getNumModules(self) -> int:
        """Returns the number of modules currently defined in the system."""

        self.cnumMod = c_int(0)
        self.status = self._lib.xiaGetNumModules(byref(self.cnumMod))
        if self.status == 0:
            self.CHECK_ERROR(f"There are currently {self.cnumMod.value} detectors defined")
        else:
            self.CHECK_ERROR("Could not read get num defined modules.")

        return self.cnumMod.value
    
    def getNumberOfPeakingTimes(self) -> c_double:
        """Returns number of peaking times."""
        
        cnPeakingTimesPerFippi = c_short()
        self.status = self._lib.xiaBoardOperation(self.cdetChan, self.stringToBytes("get_number_pt_per_fippi"), byref(cnPeakingTimesPerFippi))
        self.CHECK_ERROR(f"Getting number of peaking times per fippi... {cnPeakingTimesPerFippi.value}")
        
        ccurrentPeakingTimes = (c_double * cnPeakingTimesPerFippi.value)()
        self.status = self._lib.xiaBoardOperation(self.cdetChan, self.stringToBytes("get_current_peaking_times"), byref(ccurrentPeakingTimes))
        self.CHECK_ERROR(f"Getting current peaking times...")
        
        return ccurrentPeakingTimes