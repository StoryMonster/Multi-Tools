import queue
import os

class FileSelector:
    def __init__(self):
        self.files = queue.Queue()
        self.checking_file = None
        self.abandoned_files = []
        self.selected_files = []

    def _are_all_files_checked(self):
        return self.files.empty()

    def _clear_all_data(self):
        self.checking_file = None
        self.abandoned_files = []
        self.selected_files = []
        while not self.files.empty():
            self.files.get_nowait()

    def _store_files_to_check(self, content):
        lines = content.split("\n")
        for line in lines:
            filename = line.strip()
            if os.path.isfile(filename):
                self.files.put_nowait(filename)

    def handle_post_request(self, req):
        filename = req["filename"]
        status = req["status"]
        content = req["content"]
        if self.checking_file is None:
            self._store_files_to_check(content)
            return
        if status == "selected":
            self.selected_files.append(self.checking_file)
        elif status == "abandoned":
            self.abandoned_files.append(self.checking_file)

    def build_response(self):
        if self._are_all_files_checked():
            content = "selected files:\n"
            str_selected_files = "\n".join(self.selected_files)
            content += str_selected_files
            str_abandoned_files = "\n".join(self.abandoned_files)
            content += "\n\nabandoned files:\n"
            content += str_abandoned_files
            self._clear_all_data()
            return {"filename": "", "content": content}
        lines = []
        self.checking_file = self.files.get_nowait()
        with open(self.checking_file, "r") as fd:
            lines = fd.readlines()
        return {"filename": self.checking_file, "content": "".join(lines)}