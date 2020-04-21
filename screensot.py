import sys

import win32com.client
from win32api import *
from win32com import *
from win32com.client import *


def Main():

  try:

    SapGuiAuto = win32com.client.GetObject("SAPGUI")
    if not type(SapGuiAuto) == win32com.client.CDispatch:
      return

    application = SapGuiAuto.GetScriptingEngine
    if not type(application) == win32com.client.CDispatch:
      SapGuiAuto = None
      return

    connection = application.Children(0)
    if not type(connection) == win32com.client.CDispatch:
      application = None
      SapGuiAuto = None
      return

    session = connection.Children(1)
    if not type(session) == win32com.client.CDispatch:
      connection = None
      application = None
      SapGuiAuto = None
      return

   #session.findById("wnd[0]").resizeWorkingPane 173, 36, 0
    session.findById("wnd[0]").resizeWorkingPane(173, 36, 0)
   #session.findById("wnd[0]/tbar[0]/okcd").text = "/nse16"
    session.findById("wnd[0]/tbar[0]/okcd").text = "/nse16"
   #session.findById("wnd[0]").sendVKey 0
    session.findById("wnd[0]").sendVKey(0)
   #session.findById("wnd[0]/usr/ctxtDATABROWSE-TABLENAME").text = "TADIR"
    session.findById("wnd[0]/usr/ctxtDATABROWSE-TABLENAME").text = "TADIR"
   #session.findById("wnd[0]").sendVKey 0
    session.findById("wnd[0]").sendVKey(0)
   #session.findById("wnd[0]/tbar[1]/btn[8]").press
    session.findById("wnd[0]/tbar[1]/btn[8]").press()

  except:
    print(sys.exc_info()[0])

  finally:
    session = None
    connection = None
    application = None
    SapGuiAuto = None

#-Main------------------------------------------------------------------
if __name__ == "__main__":
  Main()
