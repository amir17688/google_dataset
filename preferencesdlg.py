# coding=utf-8
"""preferencesdlg.py Edit global preferences
"""

import cellprofiler.gui.help
import cellprofiler.gui.htmldialog
import cellprofiler.preferences
import matplotlib.cm
import os
import sys
import wx

DIRBROWSE = "Browse"
FILEBROWSE = "FileBrowse"
FONT = "Font"
COLOR = "Color"
CHOICE = "Choice"


class IntegerPreference(object):
    """User interface info for an integer preference

    This signals that a preference should be displayed and edited as
    an integer, optionally limited by a range.
    """

    def __init__(self, minval=None, maxval=None):
        self.minval = minval
        self.maxval = maxval


class ClassPathValidator(wx.PyValidator):
    def __init__(self):
        wx.PyValidator.__init__(self)

    def Validate(self, win):
        ctrl = self.GetWindow()
        for c in ctrl.Value:
            if ord(c) > 254:
                wx.MessageBox(
                        "Due to technical limitations, the path to the ImageJ plugins "
                        "folder cannot contain the character, \"%s\"." % c,
                        caption="Unsupported character in path name",
                        style=wx.OK | wx.ICON_ERROR, parent=win)
                ctrl.SetFocus()
                return False
        return True

    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True

    def Clone(self):
        return ClassPathValidator()


class PreferencesDlg(wx.Dialog):
    """Display a dialog for setting preferences

    The dialog handles fetching current defaults and setting the
    defaults when the user hits OK.
    """

    def __init__(self, parent=None, ID=-1, title="CellProfiler preferences",
                 size=wx.DefaultSize, pos=wx.DefaultPosition,
                 style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER |
                       wx.THICK_FRAME,
                 name=wx.DialogNameStr):
        wx.Dialog.__init__(self, parent, ID, title, pos, size, style, name)
        self.SetExtraStyle(wx.WS_EX_VALIDATE_RECURSIVELY)
        p = self.get_preferences()
        top_sizer = wx.BoxSizer(wx.VERTICAL)
        scrollpanel_sizer = wx.BoxSizer(wx.VERTICAL)
        scrollpanel = wx.lib.scrolledpanel.ScrolledPanel(self)
        scrollpanel.SetMinSize((800, 600))
        scrollpanel_sizer.Add(scrollpanel, 1, wx.EXPAND)
        scrollpanel.SetSizer(top_sizer)
        self.SetSizer(scrollpanel_sizer)

        sizer = wx.GridBagSizer(len(p), 4)
        sizer.SetFlexibleDirection(wx.HORIZONTAL)
        top_sizer.Add(sizer, 1, wx.EXPAND | wx.ALL, 5)
        index = 0
        controls = []
        help_bitmap = wx.ArtProvider.GetBitmap(wx.ART_HELP,
                                               wx.ART_CMN_DIALOG,
                                               (16, 16))
        for text, getter, setter, ui_info, help_text in p:
            text_ctl = wx.StaticText(scrollpanel, label=text)
            sizer.Add(text_ctl, (index, 0))
            if (getattr(ui_info, "__getitem__", False) and not
            isinstance(ui_info, str)):
                ctl = wx.ComboBox(scrollpanel, -1,
                                  choices=ui_info, style=wx.CB_READONLY)
                ctl.SetStringSelection(getter())
            elif ui_info == COLOR:
                ctl = wx.Panel(scrollpanel, -1, style=wx.BORDER_SUNKEN)
                ctl.BackgroundColour = getter()
            elif ui_info == CHOICE:
                ctl = wx.CheckBox(scrollpanel, -1)
                ctl.Value = getter()
            elif isinstance(ui_info, IntegerPreference):
                minval = (-sys.maxint if ui_info.minval is None
                          else ui_info.minval)
                maxval = (sys.maxint if ui_info.maxval is None
                          else ui_info.maxval)
                ctl = wx.SpinCtrl(scrollpanel,
                                  min=minval,
                                  max=maxval,
                                  initial=getter())
            else:
                if getter == cellprofiler.preferences.get_ij_plugin_directory:
                    validator = ClassPathValidator()
                else:
                    validator = wx.DefaultValidator
                current = getter()
                if current is None:
                    current = ""
                ctl = wx.TextCtrl(scrollpanel, -1, current,
                                  validator=validator)
                min_height = ctl.GetMinHeight()
                min_width = ctl.GetTextExtent("Make sure the window can display this")[0]
                ctl.SetMinSize((min_width, min_height))
            controls.append(ctl)
            sizer.Add(ctl, (index, 1), flag=wx.EXPAND)
            if ui_info == DIRBROWSE:
                def on_press(event, ctl=ctl, parent=self):
                    dlg = wx.DirDialog(parent)
                    dlg.Path = ctl.Value
                    if dlg.ShowModal() == wx.ID_OK:
                        ctl.Value = dlg.Path
                        dlg.Destroy()
            elif (isinstance(ui_info, basestring) and
                      ui_info.startswith(FILEBROWSE)):
                def on_press(event, ctl=ctl, parent=self, ui_info=ui_info):
                    dlg = wx.FileDialog(parent)
                    dlg.Path = ctl.Value
                    if len(ui_info) > len(FILEBROWSE) + 1:
                        dlg.Wildcard = ui_info[(len(FILEBROWSE) + 1):]
                    if dlg.ShowModal() == wx.ID_OK:
                        ctl.Value = dlg.Path
                    dlg.Destroy()

                ui_info = "Browse"
            elif ui_info == FONT:
                def on_press(event, ctl=ctl, parent=self):
                    name, size = ctl.Value.split(",")
                    fd = wx.FontData()
                    fd.SetInitialFont(wx.FFont(float(size),
                                               wx.FONTFAMILY_DEFAULT,
                                               face=name))
                    dlg = wx.FontDialog(parent, fd)
                    if dlg.ShowModal() == wx.ID_OK:
                        fd = dlg.GetFontData()
                        font = fd.GetChosenFont()
                        name = font.GetFaceName()
                        size = font.GetPointSize()
                        ctl.Value = "%s, %f" % (name, size)
                    dlg.Destroy()
            elif ui_info == COLOR:
                def on_press(event, ctl=ctl, parent=self):
                    color = wx.GetColourFromUser(self, ctl.BackgroundColour)
                    if any([x != -1 for x in color.Get()]):
                        ctl.BackgroundColour = color
                        ctl.Refresh()
            else:
                on_press = None
            if not on_press is None:
                identifier = wx.NewId()
                button = wx.Button(scrollpanel, identifier, ui_info)
                self.Bind(wx.EVT_BUTTON, on_press, button, identifier)
                sizer.Add(button, (index, 2))
            button = wx.Button(scrollpanel, -1, '?', (0, 0), (30, -1))

            def on_help(event, help_text=help_text):
                dlg = cellprofiler.gui.htmldialog.HTMLDialog(self, "Preferences help", help_text)
                dlg.Show()

            sizer.Add(button, (index, 3))
            self.Bind(wx.EVT_BUTTON, on_help, button)
            index += 1

        sizer.AddGrowableCol(1, 10)
        sizer.AddGrowableCol(3, 1)

        top_sizer.Add(wx.StaticLine(scrollpanel), 0, wx.EXPAND | wx.ALL, 2)
        btnsizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        self.Bind(wx.EVT_BUTTON, self.save_preferences, id=wx.ID_OK)

        scrollpanel_sizer.Add(
                btnsizer, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)
        scrollpanel.SetupScrolling(scrollToTop=False)
        self.Fit()
        self.controls = controls

    def save_preferences(self, event):
        event.Skip()
        p = self.get_preferences()
        for control, (text, getter, setter, ui_info, help_text) in \
                zip(self.controls, p):
            if ui_info == COLOR:
                value = control.BackgroundColour
            elif ui_info == FILEBROWSE:
                value = control.Value
                if not os.path.isfile(value):
                    continue
            elif ui_info == DIRBROWSE:
                value = control.Value
                if not os.path.isdir(value):
                    continue
            else:
                value = control.Value
            if value != getter():
                setter(value)

    def get_preferences(self):
        """Get the list of preferences.

        Each row in the list has the following form:
        Title - the text that appears to the right of the edit box
        get_function - retrieves the persistent preference value
        set_function - sets the preference value
        display - If this is a list, it represents the valid choices.
                  If it is "dirbrowse", put a directory browse button
                  to the right of the edit box.
        """
        cmaps = list(matplotlib.cm.datad.keys())
        cmaps.sort()
        return [["Default Input Folder",
                 cellprofiler.preferences.get_default_image_directory,
                 cellprofiler.preferences.set_default_image_directory,
                 DIRBROWSE, cellprofiler.gui.help.DEFAULT_IMAGE_FOLDER_HELP],
                ["Default Output Folder",
                 cellprofiler.preferences.get_default_output_directory,
                 cellprofiler.preferences.set_default_output_directory,
                 DIRBROWSE, cellprofiler.gui.help.DEFAULT_OUTPUT_FOLDER_HELP],
                ["Table font",
                 self.get_table_font,
                 self.set_table_font,
                 FONT, cellprofiler.gui.help.TABLE_FONT_HELP],
                ["Default colormap",
                 cellprofiler.preferences.get_default_colormap,
                 cellprofiler.preferences.set_default_colormap,
                 cmaps, cellprofiler.gui.help.DEFAULT_COLORMAP_HELP],
                ["Error color",
                 cellprofiler.preferences.get_error_color,
                 cellprofiler.preferences.set_error_color,
                 COLOR, cellprofiler.gui.help.ERROR_COLOR_HELP],
                ["Primary outline color",
                 cellprofiler.preferences.get_primary_outline_color,
                 cellprofiler.preferences.set_primary_outline_color,
                 COLOR, cellprofiler.gui.help.PRIMARY_OUTLINE_COLOR_HELP],
                ["Secondary outline color",
                 cellprofiler.preferences.get_secondary_outline_color,
                 cellprofiler.preferences.set_secondary_outline_color,
                 COLOR, cellprofiler.gui.help.SECONDARY_OUTLINE_COLOR_HELP],
                ["Tertiary outline color",
                 cellprofiler.preferences.get_tertiary_outline_color,
                 cellprofiler.preferences.set_tertiary_outline_color,
                 COLOR, cellprofiler.gui.help.TERTIARY_OUTLINE_COLOR_HELP],
                ["Interpolation mode",
                 cellprofiler.preferences.get_interpolation_mode,
                 cellprofiler.preferences.set_interpolation_mode,
                 [cellprofiler.preferences.IM_NEAREST, cellprofiler.preferences.IM_BILINEAR, cellprofiler.preferences.IM_BICUBIC],
                 cellprofiler.gui.help.INTERPOLATION_MODE_HELP],
                ["Intensity normalization",
                 cellprofiler.preferences.get_intensity_mode,
                 cellprofiler.preferences.set_intensity_mode,
                 [cellprofiler.preferences.INTENSITY_MODE_RAW, cellprofiler.preferences.INTENSITY_MODE_NORMAL,
                  cellprofiler.preferences.INTENSITY_MODE_LOG],
                 cellprofiler.gui.help.INTENSITY_MODE_HELP],
                ["CellProfiler plugins directory",
                 cellprofiler.preferences.get_plugin_directory,
                 cellprofiler.preferences.set_plugin_directory,
                 DIRBROWSE, cellprofiler.gui.help.PLUGINS_DIRECTORY_HELP],
                ["ImageJ plugins directory",
                 cellprofiler.preferences.get_ij_plugin_directory,
                 cellprofiler.preferences.set_ij_plugin_directory,
                 DIRBROWSE, cellprofiler.gui.help.IJ_PLUGINS_DIRECTORY_HELP],
                ["Display welcome text on startup",
                 cellprofiler.preferences.get_startup_blurb,
                 cellprofiler.preferences.set_startup_blurb,
                 CHOICE, cellprofiler.gui.help.SHOW_STARTUP_BLURB_HELP],
                ["Warn if Java runtime environment not present",
                 cellprofiler.preferences.get_report_jvm_error,
                 cellprofiler.preferences.set_report_jvm_error,
                 CHOICE, cellprofiler.gui.help.REPORT_JVM_ERROR_HELP],
                ['Show the "Analysis complete" message at the end of a run',
                 cellprofiler.preferences.get_show_analysis_complete_dlg,
                 cellprofiler.preferences.set_show_analysis_complete_dlg,
                 CHOICE, cellprofiler.gui.help.SHOW_ANALYSIS_COMPLETE_HELP],
                ['Show the "Exiting test mode" message',
                 cellprofiler.preferences.get_show_exiting_test_mode_dlg,
                 cellprofiler.preferences.set_show_exiting_test_mode_dlg,
                 CHOICE, cellprofiler.gui.help.SHOW_EXITING_TEST_MODE_HELP],
                ['Warn if images are different sizes',
                 cellprofiler.preferences.get_show_report_bad_sizes_dlg,
                 cellprofiler.preferences.set_show_report_bad_sizes_dlg,
                 CHOICE, cellprofiler.gui.help.SHOW_REPORT_BAD_SIZES_DLG_HELP],
                ['Show the sampling menu',
                 cellprofiler.preferences.get_show_sampling,
                 cellprofiler.preferences.set_show_sampling,
                 CHOICE, """<p>Show the sampling menu </p>
                 <p><i>Note that CellProfiler must be restarted after setting.</i></p>
                 <p>The sampling menu is an interplace for Paramorama, a plugin for an interactive visualization
                 program for exploring the parameter space of image analysis algorithms.
                 will generate a text file, which specifies: (1) all unique combinations of
                 the sampled parameter values; (2) the mapping from each combination of parameter values to
                 one or more output images; and (3) the actual output images.</p>
                 <p>More information on how to use the plugin can be found
                 <a href="http://www.comp.leeds.ac.uk/scsajp/applications/paramorama2/">here</a>.</p>
                 <p><b>References</b>
                 <ul>
                 <li>Visualization of parameter space for image analysis. Pretorius AJ, Bray MA, Carpenter AE
                 and Ruddle RA. (2011) IEEE Transactions on Visualization and Computer Graphics, 17(12), 2402-2411.</li>
                 </ul>"""],
                ['Use more figure space',
                 cellprofiler.preferences.get_use_more_figure_space,
                 cellprofiler.preferences.set_use_more_figure_space,
                 CHOICE,
                 cellprofiler.gui.help.USE_MORE_FIGURE_SPACE_HELP
                 ],
                ['Maximum number of workers',
                 cellprofiler.preferences.get_max_workers,
                 cellprofiler.preferences.set_max_workers,
                 IntegerPreference(1, cellprofiler.preferences.default_max_workers() * 4),
                 cellprofiler.gui.help.MAX_WORKERS_HELP],
                ['Temporary folder',
                 cellprofiler.preferences.get_temporary_directory,
                 (lambda x: cellprofiler.preferences.set_temporary_directory(x, globally=True)),
                 DIRBROWSE,
                 cellprofiler.gui.help.TEMP_DIR_HELP],
                ['Maximum memory for Java (MB)',
                 cellprofiler.preferences.get_jvm_heap_mb,
                 cellprofiler.preferences.set_jvm_heap_mb,
                 IntegerPreference(128, 64000),
                 cellprofiler.gui.help.JVM_HEAP_HELP],
                ['Save pipeline and/or file list in addition to project',
                 cellprofiler.preferences.get_save_pipeline_with_project,
                 cellprofiler.preferences.set_save_pipeline_with_project,
                 cellprofiler.preferences.SPP_ALL,
                 cellprofiler.gui.help.SAVE_PIPELINE_WITH_PROJECT_HELP],
                ['Folder name regular expression guesses',
                 cellprofiler.preferences.get_pathname_re_guess_file,
                 cellprofiler.preferences.set_pathname_re_guess_file,
                 FILEBROWSE,
                 cellprofiler.gui.help.FOLDER_RE_GUESS_HELP],
                ['File name regular expression guesses',
                 cellprofiler.preferences.get_filename_re_guess_file,
                 cellprofiler.preferences.set_filename_re_guess_file,
                 FILEBROWSE,
                 cellprofiler.gui.help.FILE_RE_GUESS_HELP],
                ['Batch Profiler URL',
                 cellprofiler.preferences.get_batchprofiler_url,
                 cellprofiler.preferences.set_batchprofiler_url,
                 None,
                 cellprofiler.gui.help.BATCHPROFILER_URL_HELP],
                ["Pony",
                 cellprofiler.preferences.get_wants_pony,
                 cellprofiler.preferences.set_wants_pony,
                 CHOICE,
                 "Pony"
                ]]

    @staticmethod
    def get_title_font():
        return "%s,%f" % (cellprofiler.preferences.get_title_font_name(),
                          cellprofiler.preferences.get_title_font_size())

    @staticmethod
    def set_title_font(font):
        name, size = font.split(",")
        cellprofiler.preferences.set_title_font_name(name)
        cellprofiler.preferences.set_title_font_size(float(size))

    @staticmethod
    def get_table_font():
        return "%s,%f" % (cellprofiler.preferences.get_table_font_name(),
                          cellprofiler.preferences.get_table_font_size())

    @staticmethod
    def set_table_font(font):
        name, size = font.split(",")
        cellprofiler.preferences.set_table_font_name(name)
        cellprofiler.preferences.set_table_font_size(float(size))
