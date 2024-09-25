import dataclasses
import random
import time
import winreg
from threading import Thread
from functools import partial

import psutil
import requests
import json
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import socketio
from fastapi.middleware.cors import CORSMiddleware
import time
from rpa.rpa_runner import RunningRPA

import logging

import sys
import os

root_path = os.getcwd()
sys.path.append(root_path)

# sys.stdout.isatty = lambda: False

from fastapi import FastAPI
import os,sys,uvicorn


sio = None
from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from windoor import MainWindow
import global_var
BASE_DIR = os.path.join(os.environ['LOCALAPPDATA'], f"MktLogin")
class MktServerApp():
  def __init__(self, mainWindow):
    self.access_token = ""
    self._main_window: MainWindow = mainWindow

    
  def start(self):
   
    self.app = FastAPI()
    private_app = FastAPI()
    api = FastAPI(title='MKT API', openapi_url='/openapi.json', docs_url='/docs',
    description='MktLogin api documentation', version='1.0.0')
    private_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],  
        allow_headers=["*"],
    )
    sio = socketio.AsyncServer(
                cors_allowed_origins= "*",
                async_mode="asgi",
                logger=False,
                engineio_logger=False,
            )
    @sio.on('connect')
    async def connect(sid, *args, **kwargs):
        #print('connect')
        pass
        
    # Mount a separate web application at '/private_app' on main application.
    self.app.mount("/private_app", private_app)

    # Mount API sub-application at '/api' on main application. 
    # This can be useful for versioning APIs or separating admin interfaces etc.
    self.app.mount("/api", api)

    # Mount WebSocket sub-application at '/ws' using socketio's ASGIApp wrapper around `sio` object.
    # This allows handling of WebSocket connections under the '/ws' endpoint.
    self.app.mount("/ws", socketio.ASGIApp(sio))

    @sio.on('CreateNewTask')
    def CreateNewTask(self, data):
      print("createnewtask", data)
      data = json.dumps({
        "name": data["name"],
        "description": data["description"] if data["description"] != "" else "--",
        "content": self._main_window.browserUtils.encrypt(self._main_window.info_workspace["user_creator"]['username'], data["content"])
      })
      response = self._main_window.mktLoginApi.post_create_workflows(data)
      #print(response)
      return response

    @sio.on('addEvent')
    async def addEvent(self, data):
      block_name = ""
      #print("server  --------------------- ", data)
      #print("type(data)  --------------------- ", type(data))
      data = json.loads(data)
      #print("type(data)  --------------------- ", type(data))

      match data['command']:
        case "open":
          jsonblock = {
            "field": [
                {
                    "_name": "url",
                    "__text": data.get('value'),
                },
                {
                    "_name": "timeout",
                    "__text": "3",
                },
                {
                    "_name": "description"
                }
            ],
            "_type": 'cmd_page_operation_open_url'
          }
        case "delay":
          jsonblock = {
            "field":
              {
                "_name":"timeout",
                "__text":data.get('timeout')
              },
              "_type":"rpa_delay"
            }

        case "click":
          jsonblock = {
            "field": [
                {
                    "_name": "xpath",
                    "__text": data.get('targets')[0],
                },
                {
                    "_name": "timeout",
                    "__text": "3",
                },
                {
                    "_name": "description"
                },
                {
                    "_name": "id"
                },
                {
                    "_name": "name"
                },
                {
                    "_name": "class"
                },
                {
                    "_name": "text_re"
                }
            ],
            "_type": 'cmd_page_operation_click'
          }
    
        case "type":
           jsonblock = {
            "field":  [
                {
                    "_name": "id"
                  },
                  {
                    "_name": "name"
                  },
                  {
                    "_name": "class"
                  },
                  {
                    "_name": "xpath",
                    "__text": data.get('targets')[0],
                  },
                  {
                    "_name": "text_re"
                  },
                  {
                    "_name": "description"
                  }
            ],
           "value": {
                  "block": {
                    "field": {
                      "_name": "TEXT",
                      "__text": data.get('value')
                    },
                    "_type": "text"
                  },
                  "_name": "value"
                },
           "_type": "cmd_page_operation_type"
            }

        case "scroll":
          jsonblock = {
            "field": [
                {
                    "_name": "scroll_from",
                    "__text": data.get('scroll_from'),
                },
                {
                    "_name": "scroll_to",
                    "__text": data.get('scroll_to'),
                },
                {
                    "_name": "description"
                }
            ],
            "_type": 'cmd_page_operation_scroll'
          }
        case "submit":
          block_name = 'cmd_page_operation_submit'
          # block_name = 'cmd_page_operation'
        case "clickAndWait": 
          block_name = 'cmd_page_operation_click_and_wait'
        case "new_tab":
          block_name = 'cmd_page_operation_new_tab'
        case "close_tab": 
          block_name = 'cmd_page_operation_close_tab'
        case "close_other_tab":
          block_name = 'cmd_page_operation_close_other_tab'
        case "switch_tab":
          block_name = 'cmd_page_operation_switch_tab'
        case "refresh":
          block_name = 'cmd_page_operation_refresh'
          fields = [
                {
                    "_name": "timeout",
                    "__text": data.get('timeout'),
                },
                {
                    "_name": "description"
                }
            ]
        case "go_back":
          block_name = 'cmd_page_operation_go_back'
        case "go_foward":
          block_name = 'cmd_page_operation_go_foward'
        case "screenshot":
          block_name = 'cmd_page_operation_screenshot'
        case "selectWindow":
          block_name = 'cmd_page_operation_select_window'
        case "selectFrame":
          block_name = 'cmd_page_operation_select_frame'
        case "sendkeys":
          block_name = 'cmd_page_operation_sendkeys'
        case "sendchar":
          block_name = 'cmd_page_operation_sendchar'
        case _:
          #print(f"Block {data['command']} is in development")
          pass
      

      await  sio.emit("ClientUpdateUi", jsonblock, broadcast=True) 
    @sio.on('Record')
    async def Record(self,data):
      #print("profile_id --- record", data["profile_id"])

      await sio.emit("success_status", {"status": "success","message": 'In progress open chrome record your actions.'})
      global_var.stop_record = False
      global_var.signal_mng.rpa_open_profile_signal.emit(data["profile_id"])
        
      # if int(data["profile_id"]) in global_var.arr_profile_id:
      #   emit("error_status", {
      #     "status": "error",
      #     "message": "Profile ID is invalid!"
      #   })
      # else:
      #   emit("success_status", {
      #   "status": "success",
      #   "message": 'In progress open chrome record your actions.'
      #   })
      #   global_var.stop_record = False
      #   global_var.signal_mng.rpa_open_profile_signal.emit(data["profile_id"])
        


    @sio.on('StopRecord')
    async def StopRecord(self):
      global_var.signal_mng.rpa_stop_record.emit()
      await  sio.emit("ClientUpdateUi", {"_type":"cmd_page_operation_close"}, broadcast=True) 
      await sio.emit("success_status", {"status": "success","message": 'Recording of browser actions stopped'})
     

    @sio.on('SaveMacro')
    def SaveMacro(self,data):
        #print(data)
        with open(os.path.join(os.path.abspath(''), 'current_macro.mktlogin'), 'w') as f:
          f.write(data['data'])
        return {"status": "macro saved"}
        # emit("status", data, broadcast=True)

    @sio.on('StartScript')
    async def StartScript(self, data):
        global_var.signal_mng.rpa_play_macro.emit(data)          
        await sio.emit("success_status", {"status": "success","message": 'Script started'})
      


    @sio.on('StopScript')
    async def StopMacro(self,data):
      # stop profile
      if int(data.get("profile_id")) not in global_var.list_profile_id_opened:
        await sio.emit("error_status", {"status": "error","message": "Profile not opened"})
      else:
        global_var.signal_mng.stop_profile_signal.emit(int(data.get("profile_id")))
        await sio.emit("success_status", {"status": "success","message": 'Script Stopped'})
    
      
    def rpa_browser_close(emit_data):
      global sio
      #print('llllllllllllllllllllllllllllllllllllllllll++++++++++++++++++++++++++++++++')
      #print(emit_data)
      global_var.stop_record = True
      # sio.connect('http://localhost:7195', wait=True, wait_timeout=3)
      sio.emit('RPABrowserClosed', emit_data)

    global_var.signal_mng.rpa_browser_close_signal.connect(rpa_browser_close)
    
    @private_app.get("/get-all-profiles")
    def all_profiles():
      list_id = global_var.list_name_profiles
      
      return {"data": list_id}
    

    ############################ API ####################################
    # This is a GET API endpoint to fetch all profiles.

    @api.on_event("startup")
    async def startup():
      logger = logging.getLogger(__name__)
      logger.info("Everything is going well")
      raise Exception("Nope!")

    @api.get("/")
    async def read_root():
      return {"Hello": "World"}
    
    @api.get("/profiles", summary="Get all profiles in current workspace.", description="Get all profiles in current workspace.")
    def all_profiles():
      list_profiles_currents = global_var.list_profiles_currents
      list_profiles = []
      for profile in list_profiles_currents:
        decrypt_cookie = ""
        try:
          if profile.get("cookies") is not None:
            decrypt_cookie = self._main_window.browserUtils.decrypt(profile["user_created"]['username'] , profile.get('cookies'))
        except Exception as e:
          pass
      
        list_profiles.append({"id": profile.get("id"), "name": profile.get("name"), 
                              "profile_group": profile.get("profile"), 
                              "browser_type": profile.get("browser_type"),
                              "kernel_version": profile.get("kernel_version"),
                              "proxy_mode": profile.get("proxy_mode"),
                              "proxy_type": profile.get("proxy_type"),
                              "proxy_host": profile.get("proxy_host"),
                              "proxy_port": profile.get("proxy_port"),
                              "proxy_user": profile.get("proxy_user"),
                              "proxy_password": profile.get("proxy_password"),
                              "profile_hash": profile.get("profile_hash"),
                              "date_expired": profile.get("date_expired"),
                              "duration": profile.get("duration"),
                              "last_open": profile.get("last_open"),
                              "is_run": profile.get("is_run"),
                              "created_at": profile.get("created_at"),
                              "updated_at": profile.get("updated_at"),
                              "cookies": decrypt_cookie})
      return {"data": list_profiles}
    
    # This is a GET API endpoint to fetch a specific profile by ID.
    @api.get("/profile", summary="Get a specific profile by ID", description="Get a specific profile by ID")
    def getProfile(id:int):
      profile = next((item for item in global_var.list_profiles_currents if item['id'] == id), None)
     
      if profile is not None:
        decrypt_cookie = ""
        try:
          if profile.get("cookies") is not None:
            decrypt_cookie = self._main_window.browserUtils.decrypt(profile["user_created"]['username'] , profile.get('cookies'))
        except Exception as e:
          pass
        data = { "name": profile.get("name"), 
                              "profile_group": profile.get("profile"), 
                              "browser_type": profile.get("browser_type"),
                              "kernel_version": profile.get("kernel_version"),
                              "proxy_mode": profile.get("proxy_mode"),
                              "proxy_type": profile.get("proxy_type"),
                              "proxy_host": profile.get("proxy_host"),
                              "proxy_port": profile.get("proxy_port"),
                              "proxy_user": profile.get("proxy_user"),
                              "proxy_password": profile.get("proxy_password"),
                              "profile_hash": profile.get("profile_hash"),
                              "date_expired": profile.get("date_expired"),
                              "duration": profile.get("duration"),
                              "last_open": profile.get("last_open"),
                              "is_run": profile.get("is_run"),
                              "created_at": profile.get("created_at"),
                              "updated_at": profile.get("updated_at"),
                              "cookies": decrypt_cookie}
        return {"status":"success", "data": data, "id": id}
      else:
        return {"status":"error", "message":"not found", "data":None}
    
    # This is a POST API endpoint which creates a new profile with the provided ID.
    @api.post("/profile", summary="Create a new profile", description="Create a new profile with the provided ID")
    def createProfile(id:int):
      
      return {"data": ""}
    
    
    # This is a DELETE API endpoint which deletes a profile with the provided ID.
    @api.delete("/profile", summary="Delete a profile", description="Delete a profile with the provided ID")
    def deleteProfile(id:int):

      return {"data": ""}
    
    
    @api.get("/open", summary="Open profiles", description="Open a profile with the provided ID")
    def getOpen(id:int):
      # viết code check id tông tại trong 1 object trong danh sách global_var.list_profiles_currents
      profile = next((item for item in global_var.list_profiles_currents if item['id'] == id), None)
      if profile is not None:
        if id not in global_var.list_profile_id_opened:
          global_var.signal_mng.open_profile_signal.emit(id)
          return {"id":id, "status":"success", "message":"opened"}
        else:
          return {"id":id, "status":"error", "message":"already opened"}
      else:
        return {"id":id, "status":"error", "message":"not found"}
    
    @api.get("/get-remote-url", summary="Get remote url", description="Get remote url for selenium or puppeteer")
    def getRemoteUrl(id:int):
      #print("global_var.list_ws_remote_currents ", global_var.list_ws_remote_currents )
      ws_remote = next((item for item in global_var.list_ws_remote_currents if item.get('profile_id') == id), None)
      if ws_remote is not None:
        return {"ws": ws_remote.get('ws_url'), "id": id}
      else:
        return {"id":id, "status":"error", "message":"not found"}
    
    
    @api.get("/stop", summary="Stop a profile", description="Stop a profile with the provided ID")
    def getStop(id:int):
      profile = next((item for item in global_var.list_profiles_currents if item['id'] == id), None)
      if profile is not None:
        if id not in global_var.list_profile_id_opened:
          return {"id":id, "status":"fail", "message":"already closed"}
        else:
          global_var.signal_mng.stop_profile_signal.emit(id)
          return {"id":id, "status":"success", "message":"closed"}
      else:
        return {"id":id, "status":"error", "message":"not found"}
    
    
      ##############################################################################
    @sio.on('SynchTranformer')
    async def SynchTranformer(self, data):   
        await sio.emit("send_data_synch",data, broadcast=True)

  import psutil

  def get_used_ports(self):
    used_ports = []
    for conn in psutil.net_connections():
      if conn.status == "LISTEN":
        used_ports.append(conn.laddr.port)
    return used_ports
    
  def start_flask_app(self,):
    try:
      LOCAL_API_PORT = 8001
      used_port = self.get_used_ports()
      for i in range(LOCAL_API_PORT, 9000):
        if i not in used_port:
          LOCAL_API_PORT = i
          break
      self.app.threaded=True
      self.app.debug=False
      global_var.port_api = LOCAL_API_PORT
      print("mkt port____________", LOCAL_API_PORT)

      uvicorn.run(self.app, host="localhost", port=LOCAL_API_PORT)
    except Exception as e:
      with open("loi_server.txt", "a") as f:
        import traceback
        f.write(traceback.format_exc())
        f.write(str(global_var.port_api))

  def stop_server(self):
    pass
    