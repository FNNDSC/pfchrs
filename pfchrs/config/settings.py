import os
from typing import Any, ClassVar, Type, ForwardRef
from pydantic import AnyHttpUrl, AnyUrl
from pydantic_settings import BaseSettings
from pathlib import Path
import platformdirs as pfd
import json
import pudb
from models import credentialModel


Passwd = ForwardRef("Passwd")


class AppData(BaseSettings):
    appName: str = "pfchrs"
    appAuthor: str = "FNNDSC"
    appConfigDir: Path = Path(pfd.user_config_dir(appName))
    appVaultKeyFile: Path = Path("key.txt")
    appVaultKeyStatus: Path = Path("key.json")
    appPasswdFile: Path = Path("passwd.json")
    appPasswdFP: Path = appConfigDir / appPasswdFile
    appVaultKeyFP: Path = appConfigDir / appVaultKeyFile
    appVaultStatusFP: Path = appConfigDir / appVaultKeyStatus

    def initialize(self):
        if not self.appConfigDir.exists():
            self.appConfigDir.mkdir(parents=True, exist_ok=True)


appData = AppData()
appData.initialize()


class Vault(BaseSettings):
    key: credentialModel.VaultKey = credentialModel.VaultKey()
    status: credentialModel.VaultStatus = credentialModel.VaultStatus()

    def initialize(self):
        if appData.appVaultKeyFP.exists():
            with open(appData.appVaultStatusFP, "r") as f:
                self.status = credentialModel.VaultStatus.parse_obj(json.load(f))
        if appData.appVaultKeyFP.exists():
            with open(appData.appVaultKeyFP, "r") as f:
                self.key.vaultKey = f.read()

    def save(self) -> credentialModel.VaultStatus:
        vaultStatus: credentialModel.VaultStatus = credentialModel.VaultStatus()
        try:
            with open(appData.appVaultKeyFP, "w") as f:
                f.write(self.key.vaultKey)
                vaultStatus.status = True
                vaultStatus.message = "Vault key added. "
        except Exception as e:
            vaultStatus.message = f"Error saving key: {e}"
        try:
            with open(appData.appVaultStatusFP, "w") as f:
                json.dump(self.status.dict(), f)
                vaultStatus.message += "Status updated."
        except Exception as e:
            vaultStatus.message += f"Error saving status: {e}"
        return vaultStatus

    def set(self, key: str) -> credentialModel.VaultStatus:
        if self.status.locked:
            self.status.message = "The vault is already locked and you cannot set a new key. Restart to reset."
        else:
            self.key.vaultKey = key
            self.status.locked = True
            self.status.message = (
                "The vault is now locked. Use the vaultKey to access prviliged data."
            )
            self.save()
        return self.status

    def status_get(self) -> credentialModel.VaultStatus:
        if self.status.locked:
            self.status.message = (
                "The value is already locked. Restart the server to resest."
            )
        else:
            self.status.message = (
                "The vault is currently unlocked. You can set a key ONCE."
            )
        return self.status

    def key_use(self, key: str) -> credentialModel.StatusWithMessage:
        access: credentialModel.StatusWithMessage = credentialModel.StatusWithMessage()
        if not self.status.locked:
            access.status = False
            access.message = (
                "The vault has not been locked and no key set. Set a key first."
            )
        elif key == self.key.vaultKey:
            access.status = True
            access.message = "vault unlocked"
        else:
            access.status = False
            access.message = "Incorrect vaultKey! No access is possible."
        return access


def vaultCheckLock(vault: Vault) -> None:
    if vault.key.vaultKey and not vault.status.locked:
        vault.status.locked = True
        print("Vault check: key has already been set. Vault is now LOCKED.")


class PasswdMgr(BaseSettings):
    passwdFile: Path = appData.appPasswdFP
    passwdDB: credentialModel.Passwd = credentialModel.Passwd()

    def initialize(self) -> credentialModel.Passwd:
        if self.passwdFile.exists():
            with open(self.passwdFile, "r") as f:
                self.passwdDB = credentialModel.Passwd.parse_obj(json.load(f))
        return self.passwdDB

    def save(self) -> credentialModel.CredentialsAdd:
        resp: credentialModel.CredentialsAdd = credentialModel.CredentialsAdd()
        try:
            with open(self.passwdFile, "w") as f:
                json.dump(self.passwdDB.dict(), f)
                resp.status = True
                resp.message = "PasswdDB updated."
        except Exception as e:
            resp.message = f"PasswdDB save error: {e}"
        return resp

    def entry_add(
        self, login: credentialModel.Credentials
    ) -> credentialModel.CredentialsStatus:
        store: credentialModel.CredentialsStatus = credentialModel.CredentialsAdd()
        self.passwdDB.entry[login.username] = {
            "username": login.username,
            "password": login.password,
            "cubeURL": login.cubeURL,
        }
        store = self.save()
        return store


# pudb.set_trace()
vault = Vault()
vault.initialize()
passwd = PasswdMgr()
