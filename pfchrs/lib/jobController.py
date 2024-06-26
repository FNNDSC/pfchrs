str_description = """
    This module provides some very simple shell-based job running
    methods.
"""


import subprocess
import os
import pudb
import json
import time
from pathlib import Path
from datetime import datetime
import uuid
import ast
from config import settings


def logHistoryPath_create() -> Path:
    """Creates the log directory structure and returns the path."""

    today: datetime = datetime.today()
    year_dir: str = str(today.year)
    date_dir: str = today.strftime("%Y-%m-%d")
    log_path: Path = (
        settings.appData.appConfigDir / "pfchrs-history" / year_dir / date_dir
    )
    try:
        log_path.mkdir(parents=True, exist_ok=True)  # Create parent dirs if needed
    except Exception as e:
        print(f"An error in creating the logHistoryPath occurred: {e}")
        log_path = Path("/tmp")
    return log_path


def json_parsePart(message: str) -> str:
    sanitized: str = ""
    l_message: list = message.split()
    for el in l_message:
        d_json: dict = ast.literal_eval(el.strip())
    return sanitized


class jobber:
    def __init__(self, d_args: dict):
        """Constructor for the jobber class.

        Args:
            d_args (dict): a dictionary of "arguments" (parameters) for the
                           object.
        """
        self.args = d_args.copy()
        self.execCmd: Path = Path("somefile.cmd")
        self.histlogPath: Path = Path("/tmp")
        if "verbosity" not in self.args.keys():
            self.args["verbosity"] = 0
        if "noJobLogging" not in self.args.keys():
            self.args["noJobLogging"] = False

    def v2JSONcli(self, v: str) -> str:
        """
        attempts to convert a JSON string serialization explicitly into a string
        with enclosed single quotes. If the input is not a valid JSON string, simply
        return it unchanged.

        An input string of

            '{ "key1": "value1", "key2": N, "key3": true }'

        is explicitly enclosed in embedded single quotes:

            '\'{ "key1": "value1", "key2": N, "key3": true }\''

        args:
            v(str): a value to process

        returns:
            str: cli equivalent string.
        """
        vb: str = ""
        try:
            d_dict = json.loads(v)
            vb = f"'{v}'"
        except:
            vb = "%s" % v
        return vb

    def dict2cli(self, d_dict: dict) -> str:
        """convert a dictionary into a cli conformant json string.

        an input dictionary of

            {
                'key1': 'value1',
                'key2': 'value2',
                'key3': true,
                'key4': false
            }

        is converted to a string:

            "--key1 value1 --key2 value2 --key3"

        args:
            d_dict (dict): a python dictionary to convert

        returns:
            str: cli equivalent string.
        """
        str_cli: str = ""
        for k, v in d_dict.items():
            if type(v) == bool:
                if v:
                    str_cli += "--%s " % k
            elif len(v):
                v = self.v2JSONcli(v)
                str_cli += "--%s %s " % (k, v)
        return str_cli

    def job_run(self, str_cmd: str):
        """
        running some cli process via python is cumbersome. the typical/easy
        path of

                            os.system(str_cmd)

        is deprecated and prone to hidden complexity. The preferred
        method is via subprocess, which has a cumbersome processing
        syntax. Still, this method runs the `str_cmd` and returns the
        stderr and stdout strings as well as a returncode.
        Providing readtime output of both stdout and stderr seems
        problematic. The approach here is to provide realtime
        output on stdout and only provide stderr on process completion.
        """
        d_ret: dict = {
            "stdout": "",
            "stderr": "",
            "cmd": "",
            "cwd": "",
            "returncode": 0,
        }
        str_stdoutline: str = ""
        str_stdout: str = ""

        p = subprocess.Popen(
            str_cmd.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # realtime output on stdout
        while True:
            stdout = p.stdout.readline()
            if p.poll() is not None:
                break
            if stdout:
                str_stdoutline = stdout.decode()
                if int(self.args["verbosity"]):
                    print(str_stdoutline, end="")
                str_stdout += str_stdoutline
        d_ret["cmd"] = str_cmd
        d_ret["cwd"] = os.getcwd()
        d_ret["stdout"] = str_stdout
        d_ret["stderr"] = p.stderr.read().decode()
        d_ret["returncode"] = p.returncode
        if int(self.args["verbosity"]) and len(d_ret["stderr"]):
            print("\nstderr: \n%s" % d_ret["stderr"])
        return d_ret

    async def job_runFromScript(self, str_cmd: str) -> dict:
        """run a job as a script (esp in the background).

        after much (probably unecessary pain) the best solution seemed to
        be:
            * create a shell script on the fs that contains the
              <str_cmd> and a "&"
            * run the shell script in subprocess.popen

        args:
            str_cmd (str): cli string to run

        returns:
            dict: a dictionary of exec state
        """

        def txscript_content(message: str) -> str:
            str_script: str = ""
            str_script = f"""#!/bin/bash

            {message}
            """
            str_script = "".join(str_script.split(r"\r"))
            return str_script

        def txscript_save(str_content) -> None:
            with open(self.execCmd, "w") as f:
                f.write(f"%s" % str_content)
            self.execCmd.chmod(0o755)

        def execstr_build(input: Path) -> str:
            """the histlogPath might have spaces, esp on non-Linux systems"""
            ret: str = ""
            t_parts: tuple = input.parts
            ret = "/".join(
                ['"{0}"'.format(arg) if " " in arg else arg for arg in t_parts]
            )
            return ret

        baseFileName: str = f"job-{uuid.uuid4().hex}"
        self.execCmd = logHistoryPath_create() / Path(baseFileName + ".sh")
        d_ret: dict = {"uid": "", "cmd": "", "cwd": "", "script": self.execCmd}
        # pudb.set_trace()
        # str_cmd += " &"
        txscript_save(txscript_content(str_cmd))
        execCmd: str = execstr_build(self.execCmd)
        process = subprocess.Popen(
            execCmd.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            close_fds=True,
        )
        # self.execCmd.unlink()
        d_ret["uid"] = str(os.getuid())
        d_ret["cmd"] = str_cmd
        d_ret["cwd"] = os.getcwd()
        if process:
            if process.stdout:
                d_ret["stdout"] = process.stdout.read()
            if process.stderr:
                d_ret["stderr"] = process.stderr.read()
        if process.returncode is None:
            d_ret["returncode"] = 0
        else:
            d_ret["returncode"] = int(process.returncode)
        return d_ret

    def job_stdwrite(
        self, d_job: dict, str_outputDir: str, str_prefix: str = ""
    ) -> dict:
        """
        Capture the d_job entries to respective files.
        """
        if not self.args["noJobLogging"]:
            for key in d_job.keys():
                with open("%s/%s%s" % (str_outputDir, str_prefix, key), "w") as f:
                    f.write(str(d_job[key]))
                    f.close()
        return {"status": True}
