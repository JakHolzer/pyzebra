import base64
import io
import re
import tempfile

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import (
    Button,
    Div,
    FileInput,
    Panel,
    RadioButtonGroup,
    Select,
    TextAreaInput,
    TextInput,
)

import pyzebra
from pyzebra.anatric import DATA_FACTORY_IMPLEMENTATION, REFLECTION_PRINTER_FORMATS


def create():
    config = pyzebra.AnatricConfig()

    def _load_config_file(file):
        config.load_from_file(file)

        logfile_textinput.value = config.logfile
        logfile_verbosity_select.value = config.logfile_verbosity

        filelist_type.value = config.filelist_type
        filelist_format_textinput.value = config.filelist_format
        filelist_datapath_textinput.value = config.filelist_datapath
        filelist_ranges_textareainput.value = "\n".join(map(str, config.filelist_ranges))

        crystal_sample_textinput.value = config.crystal_sample
        lambda_textinput.value = config.crystal_lambda
        zeroOM_textinput.value = config.crystal_zeroOM
        zeroSTT_textinput.value = config.crystal_zeroSTT
        zeroCHI_textinput.value = config.crystal_zeroCHI
        ub_textareainput.value = config.crystal_UB

        dataFactory_implementation_select.value = config.dataFactory_implementation
        dataFactory_dist1_textinput.value = config.dataFactory_dist1
        reflectionPrinter_format_select.value = config.reflectionPrinter_format

        set_active_widgets(config.algorithm)
        if config.algorithm == "adaptivemaxcog":
            threshold_textinput.value = config.threshold
            shell_textinput.value = config.shell
            steepness_textinput.value = config.steepness
            duplicateDistance_textinput.value = config.duplicateDistance
            maxequal_textinput.value = config.maxequal
            aps_window_textinput.value = str(tuple(map(int, config.aps_window.values())))

        elif config.algorithm == "adaptivedynamic":
            adm_window_textinput.value = str(tuple(map(int, config.adm_window.values())))
            border_textinput.value = str(tuple(map(int, config.border.values())))
            minWindow_textinput.value = str(tuple(map(int, config.minWindow.values())))
            reflectionFile_textinput.value = config.reflectionFile
            targetMonitor_textinput.value = config.targetMonitor
            smoothSize_textinput.value = config.smoothSize
            loop_textinput.value = config.loop
            minPeakCount_textinput.value = config.minPeakCount
            displacementCurve_textinput.value = "\n".join(map(str, config.displacementCurve))
        else:
            raise ValueError("Unknown processing mode.")

    def set_active_widgets(implementation):
        if implementation == "adaptivemaxcog":
            mode_radio_button_group.active = 0
            disable_adaptivemaxcog = False
            disable_adaptivedynamic = True

        elif implementation == "adaptivedynamic":
            mode_radio_button_group.active = 1
            disable_adaptivemaxcog = True
            disable_adaptivedynamic = False
        else:
            raise ValueError("Implementation can be either 'adaptivemaxcog' or 'adaptivedynamic'")

        threshold_textinput.disabled = disable_adaptivemaxcog
        shell_textinput.disabled = disable_adaptivemaxcog
        steepness_textinput.disabled = disable_adaptivemaxcog
        duplicateDistance_textinput.disabled = disable_adaptivemaxcog
        maxequal_textinput.disabled = disable_adaptivemaxcog
        aps_window_textinput.disabled = disable_adaptivemaxcog

        adm_window_textinput.disabled = disable_adaptivedynamic
        border_textinput.disabled = disable_adaptivedynamic
        minWindow_textinput.disabled = disable_adaptivedynamic
        reflectionFile_textinput.disabled = disable_adaptivedynamic
        targetMonitor_textinput.disabled = disable_adaptivedynamic
        smoothSize_textinput.disabled = disable_adaptivedynamic
        loop_textinput.disabled = disable_adaptivedynamic
        minPeakCount_textinput.disabled = disable_adaptivedynamic
        displacementCurve_textinput.disabled = disable_adaptivedynamic

    upload_div = Div(text="Open XML configuration file:")

    def upload_button_callback(_attr, _old, new):
        with io.BytesIO(base64.b64decode(new)) as file:
            _load_config_file(file)

    upload_button = FileInput(accept=".xml")
    upload_button.on_change("value", upload_button_callback)

    # General parameters
    # ---- logfile
    def logfile_textinput_callback(_attr, _old, new):
        config.logfile = new

    logfile_textinput = TextInput(title="Logfile:", value="logfile.log", width=520)
    logfile_textinput.on_change("value", logfile_textinput_callback)

    def logfile_verbosity_select_callback(_attr, _old, new):
        config.logfile_verbosity = new

    logfile_verbosity_select = Select(
        title="verbosity:", options=["0", "5", "10", "15", "30"], width=70
    )
    logfile_verbosity_select.on_change("value", logfile_verbosity_select_callback)

    # ---- FileList
    def filelist_type_callback(_attr, _old, new):
        config.filelist_type = new

    filelist_type = Select(title="File List:", options=["TRICS", "SINQ"], width=100)
    filelist_type.on_change("value", filelist_type_callback)

    def filelist_format_textinput_callback(_attr, _old, new):
        config.filelist_format = new

    filelist_format_textinput = TextInput(title="format:", width=490)
    filelist_format_textinput.on_change("value", filelist_format_textinput_callback)

    def filelist_datapath_textinput_callback(_attr, _old, new):
        config.filelist_datapath = new

    filelist_datapath_textinput = TextInput(title="datapath:")
    filelist_datapath_textinput.on_change("value", filelist_datapath_textinput_callback)

    def filelist_ranges_textareainput_callback(_attr, _old, new):
        ranges = []
        for line in new.splitlines():
            ranges.append(re.findall(r"\b\d+\b", line))
        config.filelist_ranges = ranges

    filelist_ranges_textareainput = TextAreaInput(title="ranges:", height=100)
    filelist_ranges_textareainput.on_change("value", filelist_ranges_textareainput_callback)

    # ---- crystal
    def crystal_sample_textinput_callback(_attr, _old, new):
        config.crystal_sample = new

    crystal_sample_textinput = TextInput(title="Sample Name:")
    crystal_sample_textinput.on_change("value", crystal_sample_textinput_callback)

    def lambda_textinput_callback(_attr, _old, new):
        config.crystal_lambda = new

    lambda_textinput = TextInput(title="lambda:", width=140)
    lambda_textinput.on_change("value", lambda_textinput_callback)

    def ub_textareainput_callback(_attr, _old, new):
        config.crystal_UB = new

    ub_textareainput = TextAreaInput(title="UB matrix:", height=100)
    ub_textareainput.on_change("value", ub_textareainput_callback)

    def zeroOM_textinput_callback(_attr, _old, new):
        config.crystal_zeroOM = new

    zeroOM_textinput = TextInput(title="zeroOM:", width=140)
    zeroOM_textinput.on_change("value", zeroOM_textinput_callback)

    def zeroSTT_textinput_callback(_attr, _old, new):
        config.crystal_zeroSTT = new

    zeroSTT_textinput = TextInput(title="zeroSTT:", width=140)
    zeroSTT_textinput.on_change("value", zeroSTT_textinput_callback)

    def zeroCHI_textinput_callback(_attr, _old, new):
        config.crystal_zeroCHI = new

    zeroCHI_textinput = TextInput(title="zeroCHI:", width=140)
    zeroCHI_textinput.on_change("value", zeroCHI_textinput_callback)

    # ---- DataFactory
    def dataFactory_implementation_select_callback(_attr, _old, new):
        config.dataFactory_implementation = new

    dataFactory_implementation_select = Select(
        title="DataFactory implementation:", options=DATA_FACTORY_IMPLEMENTATION, width=300,
    )
    dataFactory_implementation_select.on_change("value", dataFactory_implementation_select_callback)

    def dataFactory_dist1_textinput_callback(_attr, _old, new):
        config.dataFactory_dist1 = new

    dataFactory_dist1_textinput = TextInput(title="dist1:", width=290)
    dataFactory_dist1_textinput.on_change("value", dataFactory_dist1_textinput_callback)

    # ---- BackgroundProcessor

    # ---- DetectorEfficency

    # ---- ReflectionPrinter
    def reflectionPrinter_format_select_callback(_attr, _old, new):
        config.reflectionPrinter_format = new

    reflectionPrinter_format_select = Select(
        title="ReflectionPrinter format:", options=REFLECTION_PRINTER_FORMATS, width=300,
    )
    reflectionPrinter_format_select.on_change("value", reflectionPrinter_format_select_callback)

    # Adaptive Peak Detection (adaptivemaxcog)
    # ---- threshold
    def threshold_textinput_callback(_attr, _old, new):
        config.threshold = new

    threshold_textinput = TextInput(title="Threshold:")
    threshold_textinput.on_change("value", threshold_textinput_callback)

    # ---- shell
    def shell_textinput_callback(_attr, _old, new):
        config.shell = new

    shell_textinput = TextInput(title="Shell:")
    shell_textinput.on_change("value", shell_textinput_callback)

    # ---- steepness
    def steepness_textinput_callback(_attr, _old, new):
        config.steepness = new

    steepness_textinput = TextInput(title="Steepness:")
    steepness_textinput.on_change("value", steepness_textinput_callback)

    # ---- duplicateDistance
    def duplicateDistance_textinput_callback(_attr, _old, new):
        config.duplicateDistance = new

    duplicateDistance_textinput = TextInput(title="Duplicate Distance:")
    duplicateDistance_textinput.on_change("value", duplicateDistance_textinput_callback)

    # ---- maxequal
    def maxequal_textinput_callback(_attr, _old, new):
        config.maxequal = new

    maxequal_textinput = TextInput(title="Max Equal:")
    maxequal_textinput.on_change("value", maxequal_textinput_callback)

    # ---- window
    def aps_window_textinput_callback(_attr, _old, new):
        config.aps_window = dict(zip(("x", "y", "z"), re.findall(r"\b\d+\b", new)))

    aps_window_textinput = TextInput(title="Window (x, y, z):")
    aps_window_textinput.on_change("value", aps_window_textinput_callback)

    # Adaptive Dynamic Mask Integration (adaptivedynamic)
    # ---- window
    def adm_window_textinput_callback(_attr, _old, new):
        config.adm_window = dict(zip(("x", "y", "z"), re.findall(r"\b\d+\b", new)))

    adm_window_textinput = TextInput(title="Window (x, y, z):")
    adm_window_textinput.on_change("value", adm_window_textinput_callback)

    # ---- border
    def border_textinput_callback(_attr, _old, new):
        config.border = dict(zip(("x", "y", "z"), re.findall(r"\b\d+\b", new)))

    border_textinput = TextInput(title="Border (x, y, z):")
    border_textinput.on_change("value", border_textinput_callback)

    # ---- minWindow
    def minWindow_textinput_callback(_attr, _old, new):
        config.minWindow = dict(zip(("x", "y", "z"), re.findall(r"\b\d+\b", new)))

    minWindow_textinput = TextInput(title="Min Window (x, y, z):")
    minWindow_textinput.on_change("value", minWindow_textinput_callback)

    # ---- reflectionFile
    def reflectionFile_textinput_callback(_attr, _old, new):
        config.reflectionFile = new

    reflectionFile_textinput = TextInput(title="Reflection File:")
    reflectionFile_textinput.on_change("value", reflectionFile_textinput_callback)

    # ---- targetMonitor
    def targetMonitor_textinput_callback(_attr, _old, new):
        config.targetMonitor = new

    targetMonitor_textinput = TextInput(title="Target Monitor:")
    targetMonitor_textinput.on_change("value", targetMonitor_textinput_callback)

    # ---- smoothSize
    def smoothSize_textinput_callback(_attr, _old, new):
        config.smoothSize = new

    smoothSize_textinput = TextInput(title="Smooth Size:")
    smoothSize_textinput.on_change("value", smoothSize_textinput_callback)

    # ---- loop
    def loop_textinput_callback(_attr, _old, new):
        config.loop = new

    loop_textinput = TextInput(title="Loop:")
    loop_textinput.on_change("value", loop_textinput_callback)

    # ---- minPeakCount
    def minPeakCount_textinput_callback(_attr, _old, new):
        config.minPeakCount = new

    minPeakCount_textinput = TextInput(title="Min Peak Count:")
    minPeakCount_textinput.on_change("value", minPeakCount_textinput_callback)

    # ---- displacementCurve
    def displacementCurve_textinput_callback(_attr, _old, new):
        maps = []
        for line in new.splitlines():
            maps.append(re.findall(r"\d+(?:\.\d+)?", line))
        config.displacementCurve = maps

    displacementCurve_textinput = TextAreaInput(
        title="Displacement Curve (twotheta, x, y):", height=100
    )
    displacementCurve_textinput.on_change("value", displacementCurve_textinput_callback)

    def mode_radio_button_group_callback(active):
        if active == 0:
            config.algorithm = "adaptivemaxcog"
            set_active_widgets("adaptivemaxcog")
        else:
            config.algorithm = "adaptivedynamic"
            set_active_widgets("adaptivedynamic")

    mode_radio_button_group = RadioButtonGroup(
        labels=["Adaptive Peak Detection", "Adaptive Dynamic Integration"], active=0
    )
    mode_radio_button_group.on_click(mode_radio_button_group_callback)
    set_active_widgets("adaptivemaxcog")

    def process_button_callback():
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = temp_dir + "/temp.xml"
            config.save_as(temp_file)
            pyzebra.anatric(temp_file)

            with open(config.logfile) as f_log:
                output_log.value = f_log.read()

    process_button = Button(label="Process", button_type="primary")
    process_button.on_click(process_button_callback)

    output_log = TextAreaInput(title="Logfile output:", height=700, disabled=True)
    output_config = TextAreaInput(title="Current config:", height=700, width=400, disabled=True)

    tab_layout = row(
        column(
            upload_div,
            upload_button,
            row(logfile_textinput, logfile_verbosity_select),
            row(filelist_type, filelist_format_textinput),
            filelist_datapath_textinput,
            filelist_ranges_textareainput,
            crystal_sample_textinput,
            row(lambda_textinput, zeroOM_textinput, zeroSTT_textinput, zeroCHI_textinput),
            ub_textareainput,
            row(dataFactory_implementation_select, dataFactory_dist1_textinput),
            reflectionPrinter_format_select,
            process_button,
        ),
        column(
            mode_radio_button_group,
            row(
                column(
                    threshold_textinput,
                    shell_textinput,
                    steepness_textinput,
                    duplicateDistance_textinput,
                    maxequal_textinput,
                    aps_window_textinput,
                ),
                column(
                    adm_window_textinput,
                    border_textinput,
                    minWindow_textinput,
                    reflectionFile_textinput,
                    targetMonitor_textinput,
                    smoothSize_textinput,
                    loop_textinput,
                    minPeakCount_textinput,
                    displacementCurve_textinput,
                ),
            ),
        ),
        output_config,
        output_log,
    )

    async def update_config():
        config.save_as("debug.xml")
        with open("debug.xml") as f_config:
            output_config.value = f_config.read()

    curdoc().add_periodic_callback(update_config, 1000)

    return Panel(child=tab_layout, title="Anatric")
