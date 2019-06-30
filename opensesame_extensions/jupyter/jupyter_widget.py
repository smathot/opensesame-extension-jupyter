# coding=utf-8

"""
This file is part of OpenSesame.

OpenSesame is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

OpenSesame is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with OpenSesame.  If not, see <http://www.gnu.org/licenses/>.
"""

from libopensesame.py3compat import *
from libqtopensesame.misc.translate import translation_context
from libqtopensesame.widgets.base_widget import base_widget
from libqtopensesame.misc.config import cfg
from libopensesame.oslogging import oslogger
import os
import subprocess
import shlex
import time
import platform
import sys
_ = translation_context(u'jupyter', category=u'extension')


class jupyter_widget(base_widget):

    def __init__(self, main_window, jupyter):

        super(jupyter_widget, self).__init__(
            main_window,
            ui=u'extensions.jupyter.jupyter'
        )
        self._jupyter = jupyter
        self._process = None
        self.ui.button_launch.clicked.connect(self._launch)
        self.ui.button_kill.clicked.connect(self._kill)
        self._update()

    def _launch(self):

        self.main_window.set_busy(True)
        if self._running:
            oslogger.debug('jupyter-lab is already running')
            return
        try:
            self._process = subprocess.Popen(self._executable)
        except Exception as e:
            self._jupyter.notify(_(
                u'Failed to launch Jupyter Lab. '
                u'See debug window for error message.'
            ))
            self.console.write(e)
            self.main_window.set_busy(False)
        else:
            time.sleep(1)
            self._update()
            self.main_window.set_busy(False)

    def _kill(self):

        self.main_window.set_busy(True)
        if self._running:
            oslogger.debug('killing jupyter-lab')
        self._process.kill()
        time.sleep(1)
        self._update()
        self.main_window.set_busy(False)

    def _update(self):

        self.ui.button_kill.setEnabled(self._running)
        self.ui.button_launch.setEnabled(not self._running)

    @property
    def _running(self):

        return self._process is not None and self._process.poll() is None

    @property
    def _executable(self):

        if not cfg.jupyter_lab_executable:
            # On Windows, look in the Scripts subfolder, which is where
            # Anaconda puts all the executables
            if platform.system() == u"Windows":
                cmd = os.path.join(
                    os.path.dirname(sys.executable),
                    u'Scripts',
                    u'jupyter-lab.exe'
                )
                if not os.path.exists(cmd):
                    cmd = u'jupyter-lab'
            else:
                cmd = u'jupyter-lab'
        else:
            cmd = cfg.jupyter_lab_executable
        return [cmd] + shlex.split(cfg.jupyter_lab_args)
