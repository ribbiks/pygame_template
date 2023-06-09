import json
import os
import platform
import traceback

from source.globals import *

#
# save data code adapted from David Pendergast's "Alien Knightmare" project:
# - https://github.com/davidpendergast/dimensions/blob/main/src/userdata.py
#

if PYGBAG:
    from __EMSCRIPTEN__ import window


class SaveFile:
    def __init__(self, save_dir):
        self.data = {}
        self.save_key = 'pygame_savefile'
        self.save_dir = None
        if PYGBAG is False:
            self.save_dir = save_dir
            if not os.path.isdir(self.save_dir):
                os.mkdir(self.save_dir)
        self.waiting_for_uploaded_saves = False

    def copy_via_json_serialization(self, v):
        try:
            val_as_json_str = json.dumps(v)
            return json.loads(val_as_json_str)
        except Exception as e:
            print(f"ERROR: val isn't json-compatible: {v} (type is {type(v).__name__})")
            raise e

    def insert_data(self, k, v):
        try:
            self.data[k] = self.copy_via_json_serialization(v)
        except Exception as e:
            print(f"ERROR: val isn't json-compatible: {v} (type is {type(v).__name__})")
            raise e

    def get_data(self, k, coercer=lambda x: x, or_else=None):
        if k in self.data:
            v = self.data[k]
            v = self.copy_via_json_serialization(v)
            if coercer is not None:
                try:
                    return coercer(v)
                except Exception:
                    print(f"ERROR: failed to coerce user data: {k}={v} (using {or_else} instead)")
                    traceback.print_exc()
                    return or_else
            else:
                return v

    def save_data_to_disk(self, save_slot=0):
        if PYGBAG:
            blob_str = json.dumps(self.data)
            window.localStorage.setItem(self.save_key, blob_str)
            print(f"INFO: saved data to window.localStorage at \"{self.save_key}\"")
        else:
            local_filepath = os.path.join(self.save_dir, self.save_key + '_' + str(save_slot) + '.json')
            action_str = "overwrote" if os.path.exists(local_filepath) else "created"
            with open(local_filepath, 'w') as fp:
                json.dump(self.data, fp)
                print(f"INFO: {action_str} {local_filepath} with data: {self.data}")

    def load_data_from_disk(self, save_slot=0):
        if PYGBAG:
            blob_str = window.localStorage.getItem(self.save_key)
            if blob_str is not None:
                print(f"INFO: loaded \"{self.save_key}\" from window.localStorage: {blob_str}")
                self.data = json.loads(blob_str)
            else:
                print(f"INFO: no save data found in window.localStorage at \"{self.save_key}\", fresh launch?")
        else:
            local_filepath = os.path.join(self.save_dir, self.save_key + '_' + str(save_slot) + '.json')
            if os.path.exists(local_filepath):
                with open(local_filepath) as fp:
                    self.data = json.load(fp)
                    print(f"INFO: loaded data from {local_filepath}: {self.data}")
            else:
                print(f"INFO: no save data found at {local_filepath}, fresh launch?")

    #
    #
    #
    def download_save_data_from_web_to_disk(self):
        if PYGBAG:
            blob_str = json.dumps(self.data)
            js_code  = "const download = () => (\n"
            js_code += "  Object.assign(document.createElement(\"a\"), {\n"
            js_code += "    href: `data:application/JSON, ${encodeURIComponent(\n"
            js_code += "      JSON.stringify(\n"
            js_code += "        (function(){\n"
            js_code += "          const o = " + blob_str + ";\n"
            js_code += "          return o\n"
            js_code += "        }())\n"
            js_code += "        , null, 2)\n"
            js_code += "    )}`,\n"
            js_code += "    download: \"" + self.save_key + "\",\n"
            js_code += "  }).click()\n"
            js_code += ")\n"
            js_code += "download()\n"
            try:
                platform.window.eval(js_code)
            except Exception as e:
                print("ERROR: could not download save data.")
                print(e)

    #
    #
    #
    def upload_save_data_from_disk_to_web(self):
        if PYGBAG:
            js_code  = ""
            js_code += "var canvas_obj = document.getElementById('canvas');\n"
            js_code += "canvas_obj.setAttribute(\"onclick\",\"click_dlg();\");\n"
            js_code += "\n"
            js_code += "function click_dlg(){\n"
            js_code += "  document.getElementById('upload_savefile').click();\n"
            js_code += "  document.getElementById('canvas').removeAttribute(\"onclick\");\n"
            js_code += "}\n"
            try:
                platform.window.eval(js_code)
                self.waiting_for_uploaded_saves = True
            except Exception as e:
                print("ERROR: could not upload save data.")
                print(e)
                self.waiting_for_uploaded_saves = False

    def check_webstorage_for_uploaded_save(self):
        if PYGBAG and self.waiting_for_uploaded_saves:
            blob_str = window.localStorage.getItem('uploaded_save_data')
            if blob_str is not None:
                print(f"INFO: successfully read uploaded save data: {blob_str}")
                self.data = json.loads(blob_str)
                self.waiting_for_uploaded_saves = False
