import time
from rpa.mkt_automation.connection import Connection
import asyncio
import websockets
from websockets.legacy.client import connect as ws_connect
from rpa.mkt_automation.browser import Browser
from rpa.mkt_automation import helpers
from rpa.mkt_automation.frame_manager import Frame

from typing import List, Dict, Any, Optional
import json

import io
import socketio
import json
from entities.data_rpa import DataRPA

import global_var
prev_url = None
sio = socketio.Client(logger=True, engineio_logger=True)

#  _obj = await self._client.send('Runtime.callFunctionOn', {
#                 'functionDeclaration': f'{pageFunction}\n{suffix}\n',
#                 'executionContextId': self._contextId,
#                 'arguments': [self._convertArgument(arg) for arg in args],
#                 'returnByValue': False,
#                 'awaitPromise': True,
#                 'userGesture': True,
#             })

scroll_timeout = None
time_count = 0




async def is_submit_button(client, objectId) -> bool:
  isSubmitButtonResponse = await client.send('Runtime.callFunctionOn', {
    'functionDeclaration': """function isSubmitButton() {
                            return (this.tagName === 'BUTTON' &&
                                this.type === 'submit' &&
                                this.form !== null);
                            }""",
    'objectId': objectId,
  })
  return isSubmitButtonResponse["result"]['value']


async def check_unique(client, ignored: List[Dict[str, Any]], name: Optional[str] = None,
                       role: Optional[str] = None) -> bool:
  root = await client.send('DOM.getDocument', {'depth': 0})
  checkName = await client.send('Accessibility.queryAXTree', {
    'backendNodeId': root["root"]['backendNodeId'],
    'accessibleName': name,
    'role': role
  })
  ignoredIds = set(map(lambda axNode: axNode['backendDOMNodeId'], ignored))
  checkNameMinusTargetTree = list(filter(
    lambda axNode: axNode['backendDOMNodeId'] not in ignoredIds,
    checkName['nodes']
  ))
  return len(checkNameMinusTargetTree) < 2


# argv
# 
# 
# proc.exec(serverauto.exe, "khoi_code")
# poc.out(
#   kjk
#   
# )

async def get_selector(
  client,
  objectId: str
) -> Optional[str]:
  # currentObjectId = objectId
  # 
  # prevName = ''
  # while currentObjectId:
  #   queryResp = await client.send('Accessibility.queryAXTree', {
  #     'objectId': currentObjectId
  #   })
  # 
  #   targetNodes = queryResp['nodes']
  #   #print("targetNodes", targetNodes)
  #   if len(targetNodes) == 0:
  #     break
  #   axNode = targetNodes[0]
  # 
  #   #print("axNode ID", axNode['id']['value'])
  #   #print("axNode ID", axNode['class']['value'])
  # 
  #   #print("axNode", axNode)
  # 
  #   name = axNode['name']['value']
  #   role = axNode['role']['value']
  #   if not name or not prevName in name:
  #     break
  #   prevName = name
  #   break
  # 
  #   # uniqueName = await check_unique(client, targetNodes, name, "")
  #   # if name and uniqueName:
  #   #     return f'aria/{name}'
  #   # uniqueNameRole = await check_unique(client, targetNodes, name, role)
  #   # if name and role and uniqueNameRole:
  #   #     return f'aria/{name}[role="{role}"]'
  #   # elif name and uniqueNameRole:
  #   #    return f'aria/{name}'
  # 
  #   # result = await client.send('Runtime.callFunctionOn', {
  #   #     'functionDeclaration':"""function getParent() {
  #   #                                 if (this.parentNode.nodeType === Node.DOCUMENT_FRAGMENT_NODE) {
  #   #                                     return this.parentNode.host;
  #   #                                 }
  #   #                                 else {
  #   #                                     return this.parentElement;
  #   #                                 }
  #   #                             }""",
  #   #     'objectId': currentObjectId
  #   # })
  #   # currentObjectId = result['objectId']

  result = await client.send('Runtime.callFunctionOn', {
    'functionDeclaration': """
                  function XPath() {
                      var element = this;
                    var targets = [];
                    var xpaths = function (xpathToExecute) {
                        var result = [];
                        var nodesSnapshot = document.evaluate(xpathToExecute, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                        for (var i = 0; i < nodesSnapshot.snapshotLength; i++) {
                            result.push(nodesSnapshot.snapshotItem(i));
                        }
                        return result;
                    }
                    if (!(element instanceof Element))
                        return '';
                    var tagname = element.nodeName.toLowerCase();
                    if (element.id !== '')
                        targets.push(`//${tagname}[@id='${element.id}']`); ;
                    if (element.getAttribute("name") !== null) {
                        let xpath = `//${tagname}[@name='${element.getAttribute("name")}']`;
                        if (xpaths(xpath).length == 1)
                            targets.push(xpath);
                    }
                    if (element.getAttribute("href") !== null) {
                        let xpath = `//${tagname}[@href='${element.getAttribute("href")}']`;
                        if (xpaths(xpath).length == 1)
                            targets.push(xpath);
                    }
                    if (element.getAttribute("class") !== null) {
                        let xpath = `//${tagname}[@class='${element.getAttribute("class")}']`;
                        if (xpaths(xpath).length == 1)
                            targets.push(xpath); 
                    }
                    if (element.getAttribute("aria-label") !== null) {
                        let xpath = `//${tagname}[@aria-label='${element.getAttribute("aria-label")}']`;
                        if (xpaths(xpath).length == 1)
                            targets.push(xpath);
                    }
                    if (element.getAttribute("type") !== null) {
                        let xpath = `//${tagname}[@type='${element.getAttribute("type")}']`;
                        if (xpaths(xpath).length == 1)
                            targets.push(xpath);
                    }
                    const path = [];

                    while (element !== document.documentElement) {
                        let sibling = element.previousElementSibling;
                        let index = 1;

                        while (sibling) {
                            if (sibling.nodeName === element.nodeName)
                                index++;
                            sibling = sibling.previousElementSibling;
                        }

                        const nodeName = element.nodeName.toLowerCase();
                        const step = `/${nodeName}[${index}]`;
                        path.unshift(step);

                        element = element.parentElement;
                    }
                    path.unshift('/');
                    targets.push(path.join(''));
                    return targets.join(';');
                }
        """,
    'objectId': objectId
  })
  #print('result["result"]', result["result"]['value'])
  if (result["result"]['value'] != None):
    return result["result"]['value'].split(';')

  return None


def escape_selector(selector: str) -> str:
  return json.dumps(selector)


@sio.event
def connect():
  #print("Connected to server Recoder RPA")
  pass


@sio.event
def disconnect():
  #print("Disconnected from server")
  pass


async def run_recorder(ws_url, _loop):
  if not sio.connected:
    sio.connect('http://127.0.0.1:' + str(global_var.port_api), socketio_path="/ws/socket.io", wait=True, wait_timeout=3)
    sio.on('connect', connect)
    sio.on('disconnect', disconnect)

  #output = io.StringIO()
  asyncio.set_event_loop(_loop)

  _connection = Connection(ws_url, _loop, 0)
  browserContextIds = (await _connection.send('Target.getBrowserContexts')).get('browserContextIds', [])
  browser = await Browser.create(_connection, browserContextIds, False, None, None,
                                 lambda: _connection.send('Browser.close'))

  page = (await browser.pages())[0]

  client = page._client

  async def resume():
    await client.send('Debugger.setSkipAllPauses', {"skip": True})
    await skip()
    await client.send('Debugger.setSkipAllPauses', {"skip": False})

  async def find_target_id(local_frame, interesting_class_names):
    try:
      event_properties = await getPropertiesEvent(local_frame, interesting_class_names)
      target = next((prop for prop in event_properties["result"] if prop['name'] == 'target'), None)
      return target['value']['objectId'] if target else None
    except:
      pass

  async def getPropertiesEvent(local_frame, interesting_class_names):
    try:
      event = next(
        (prop for prop in local_frame if prop["value"]['className'] in interesting_class_names), None)
      if not event:
        return None
      event_properties = await page._client.send('Runtime.getProperties', {'objectId': event["value"]['objectId']})
      return event_properties
    except:
      pass

  def CalculationDelay():
    global time_count
    sio.emit('addEvent',json.dumps({"command": "delay", "timeout": str(time_count)}))
    # #print(data.to_json())

  async def handle_click_event(local_frame):
    global time_count
    CalculationDelay()

    time_count = 0
    propertiesEvent = await  getPropertiesEvent(local_frame, ['MouseEvent', 'PointerEvent'])

    target = next((prop for prop in propertiesEvent["result"] if prop['name'] == 'target'), None)
    target_id = target['value']['objectId'] if target else None
    #print(target_id)
    if not target_id:
      await skip()
      return
    if await is_submit_button(client, target_id):
      await skip()
      return
    _height_resp = await client.send('Runtime.evaluate', {"expression": 'window.innerHeight'})
    _width_resp = await client.send('Runtime.evaluate', {"expression": 'window.innerWidth'})

    clientX_items = list(filter(lambda item: item["name"] == "clientX", propertiesEvent["result"]))
    clientX_value = clientX_items[0]["value"]["value"] if clientX_items else None

    clientY_items = list(filter(lambda item: item["name"] == "clientY", propertiesEvent["result"]))
    clientY_value = clientY_items[0]["value"]["value"] if clientY_items else None

    x = "{:.2f}".format((clientX_value / _width_resp["result"]['value']) * 100)
    y = "{:.2f}".format((clientY_value / _height_resp["result"]['value']) * 100)

    selector = await get_selector(client, target_id)
    data = DataRPA("click", selector, f"{x};{y}")
    #print(data.to_json())
    sio.emit('addEvent', data.to_json())
    await resume()

  async def handle_submit_event(local_frame):
    global time_count
    target_id = await find_target_id(local_frame, ['SubmitEvent'])
    #print(target_id)
    if not target_id:
      await skip()
      return
    selector = await get_selector(client, target_id)

    CalculationDelay()
    time_count = 0
    data = DataRPA("submit", selector, "")
    #print(data.to_json())
    sio.emit('addEvent', data.to_json())
    await resume()

  async def handle_change_event(local_frame):
    global time_count
    target_id = await find_target_id(local_frame, ['Event'])

    if not target_id:
      await skip()
      return
    CalculationDelay()
    time_count = 0
    target_value = await client.send('Runtime.callFunctionOn',
                                     {"functionDeclaration": 'function() { return this.value }', "objectId": target_id})

    value = target_value["result"]['value']
    #print(value)
    selector = await get_selector(client, target_id)
    data = DataRPA("type", selector, value)
    #print(data.to_json())
    sio.emit('addEvent', data.to_json())
    await resume()

  async def handle_scroll_event():
    global scroll_timeout, time_count

    if scroll_timeout:
      await resume()
      return
    CalculationDelay()

    time_count = 0
    prev_scroll_height_resp = await client.send('Runtime.evaluate', {"expression": 'window.pageYOffset'})
    prev_scroll_width_resp = await client.send('Runtime.evaluate', {"expression": 'window.pageXOffset'})
    prev_scroll_height = prev_scroll_height_resp["result"]['value']
    prev_scroll_width = prev_scroll_width_resp["result"]['value']
    scroll_timeout = asyncio.Future()

    async def timeout():
      global scroll_timeout

      await asyncio.sleep(1)
      current_scroll_height_resp = await client.send('Runtime.evaluate', {"expression": 'window.pageYOffset'})
      current_scroll_height = current_scroll_height_resp["result"]['value']
      current_scroll_width_resp = await client.send('Runtime.evaluate', {"expression": 'window.pageXOffset'})
      current_scroll_width = current_scroll_width_resp["result"]['value']

      data = json.dumps({"command": "scroll", "scroll_from": f"{prev_scroll_width} {prev_scroll_height}", "scroll_to":f"{current_scroll_width} {current_scroll_height}"})
      sio.emit('addEvent', data)

      # if current_scroll_height > prev_scroll_height:
      #     data = {
      #         "command": "scroll",
      #         "target": "",
      #         "value": "ToBottom",
      #         "description": "",
      #         "option": ""
      #     }
      #     #print('await scrollToBottom();')
      # else:
      #     data = {
      #         "command": "scroll",
      #         "target": "",
      #         "value": "scrollToTop",
      #         "description": "",
      #         "option": ""
      #     }
      #     #print('await scrollToTop();')

      scroll_timeout = None

    asyncio.ensure_future(timeout())
    await resume()

  async def on_paused(paused_event):
    try:

      event_name = paused_event['data']['eventName']
      local_frame = paused_event['callFrames'][0]['scopeChain'][0]
      result = await client.send('Runtime.getProperties', {'objectId': local_frame['object']['objectId']})

      if event_name == 'listener:click':
        await handle_click_event(result['result'])
      elif event_name == 'listener:submit':
        await handle_submit_event(result['result'])
      elif event_name == 'listener:change':
        await handle_change_event(result['result'])
      elif event_name == 'listener:scroll':
        await handle_scroll_event()
      else:
        await skip()

    except:
      await skip()
      pass

  async def on_dom_content_loaded():
    await client.send('Debugger.enable', {})
    await client.send('DOMDebugger.setEventListenerBreakpoint', {
      'eventName': 'click',
    })
    await client.send('DOMDebugger.setEventListenerBreakpoint', {
      'eventName': 'change',
    })
    await client.send('DOMDebugger.setEventListenerBreakpoint', {
      'eventName': 'submit',
    })
    await client.send('DOMDebugger.setEventListenerBreakpoint', {
      'eventName': 'scroll',
    })

  async def timer():
    global time_count
    while True:
      await asyncio.sleep(1)
      time_count = time_count + 1

  _loop.create_task(timer())

  page.on('domcontentloaded', lambda: _loop.create_task(on_dom_content_loaded()))

  async def skip():
    await client.send('Debugger.resume', {'terminateOnResume': False})

  await page.evaluateOnNewDocument("""()=>{
        window.addEventListener('change', (event) => { }, true);
        window.addEventListener('click', (event) => { }, true);
        window.addEventListener('submit', (event) => { }, true);
        window.addEventListener('scroll', () => { }, true);
     
        }
    """)
  await page.evaluateOnNewDocument("""() => {
          if (navigator.webdriver !== undefined && navigator.webdriver === true) {
              delete Object.getPrototypeOf(navigator).webdriver
          }
      }""")


  client.on('Debugger.paused', lambda event: _loop.create_task(on_paused(event)))

  # them gi do
  def print_console_msg(msg):
        #print("console", msg.text)
        pass
  async def framenavigated(frame: Frame):
    global prev_url
    #global time_count
    #CalculationDelay()
    current_url = frame.url
    if frame == page.mainFrame:
      if not prev_url or prev_url!=current_url:
        data = DataRPA("open", None, frame.url)
        #print(data.to_json())
        sio.emit('addEvent', data.to_json())
      prev_url = current_url
      
      
  page.on('framenavigated', lambda event: _loop.create_task(framenavigated(event)));
  await page.goto('https://www.google.com/')

  while page.isClosed() == False:
    await asyncio.sleep(2)
    if global_var.stop_record == True:
      break

  sio.emit('RPABrowserClosed', 'record')
  # await asyncio.sleep(5)
  #print('sio.disconnect===============================================')
  sio.disconnect()

  return None

  # await asyncio.sleep(100000)


# _loop.create_task(main())

# tasks = asyncio.all_tasks(loop=_loop)  # Lấy danh sách tất cả các coroutine đang chạy trên EventLoop hiện tại
# _loop.run_until_complete(asyncio.gather(*tasks))

# def run_recorder(ws_url, _loop):
#   asyncio.get_event_loop().run_until_complete(run_recorder(ws_url, _loop))
  # asyncio.run(main(ws_url))
