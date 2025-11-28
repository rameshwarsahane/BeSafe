# main.py
"""
Be Safe - Kivy emergency app (Kivy prototype)
Trigger type: C (big button + screen off/power-button best-effort)
Emergency numbers (configured):
+91 7387224241
+91 7666929196
+91 9021776161
+91 7028830712

This is a prototype. Background / silent capture and guaranteed power-button detection
are not reliable on all Android devices. The code below uses a visible button and a
best-effort listener for screen OFF events (via BroadcastReceiver using pyjnius).
"""

import os
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import mainthread
from kivy.utils import platform

EMERGENCY_NUMBERS = [
    "+917387224241",
    "+917666929196",
    "+919021776161",
    "+917028830712",
]

MEDIA_DIR = '/sdcard/BeSafeMedia'
if not os.path.exists(MEDIA_DIR):
    try:
        os.makedirs(MEDIA_DIR)
    except Exception:
        pass

# Android imports guarded by platform
if platform == 'android':
    from jnius import autoclass, cast, PythonJavaClass, java_method
    from android.permissions import request_permissions, Permission
    from android import mActivity
    from plyer import camera
    # For SMS fallback
    SmsManager = autoclass('android.telephony.SmsManager')


class ScreenReceiver(PythonJavaClass):
    __javainterfaces__ = ['android/content/BroadcastReceiver']
    __javacontext__ = 'app'

    @java_method('(Landroid/content/Context;Landroid/content/Intent;)V')
    def onReceive(self, context, intent):
        try:
            action = intent.getAction()
            # Detect screen off and trigger emergency; this is best-effort only
            if action == "android.intent.action.SCREEN_OFF":
                # call the app-level trigger via App.get_running_app()
                app = App.get_running_app()
                if app:
                    app.root.on_trigger_emergency(from_screen_off=True)
        except Exception as e:
            print('ScreenReceiver error', e)


class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 12
        self.spacing = 12
        self.status = Label(text='Be Safe — Idle', size_hint=(1, 0.2))
        self.add_widget(self.status)

        self.btn = Button(text='EMERGENCY — Tap to send photo & SMS', size_hint=(1, 0.4), font_size='20sp')
        self.btn.bind(on_release=self.on_trigger_emergency)
        self.add_widget(self.btn)

        self.test_btn = Button(text='Test SMS (no photo)', size_hint=(1, 0.2))
        self.test_btn.bind(on_release=self.on_test_sms)
        self.add_widget(self.test_btn)

        # Request permissions on Android
        if platform == 'android':
            request_permissions([Permission.CAMERA, Permission.SEND_SMS, Permission.ACCESS_FINE_LOCATION, Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])
            # Register screen receiver (best-effort)
            try:
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                IntentFilter = autoclass('android.content.IntentFilter')
                activity = PythonActivity.mActivity
                self._receiver = ScreenReceiver()
                filt = IntentFilter()
                filt.addAction('android.intent.action.SCREEN_OFF')
                activity.registerReceiver(self._receiver, filt)
            except Exception as e:
                print('Could not register receiver', e)

    @mainthread
    def set_status(self, text):
        self.status.text = f'Be Safe — {text}'

    def _timestamp_filename(self):
        t = datetime.now().strftime('%Y%m%d_%H%M%S')
        return os.path.join(MEDIA_DIR, f'BESAFE_{t}.jpg')

    def on_trigger_emergency(self, instance=None, from_screen_off=False):
        # Main emergency flow: take photo (opens native camera), save file, then send SMS with file path
        self.set_status('Triggering emergency...')
        if platform == 'android':
            fname = self._timestamp_filename()
            try:
                # Use plyer camera (opens camera UI)
                camera.take_picture(filename=fname, on_complete=lambda p: self._on_photo_saved(p, from_screen_off))
                self.set_status('Camera launched — please take photo')
            except Exception as e:
                print('Camera error', e)
                # fallback: send SMS without photo
                self._send_sms_all('Emergency! (photo failed)')
                self.set_status('Photo failed; SMS sent')
        else:
            # Desktop test: create dummy file and simulate
            fname = self._timestamp_filename()
            with open(fname, 'wb') as f:
                f.write(b'SIMULATED')
            self._on_photo_saved(fname, from_screen_off)

    def _on_photo_saved(self, path, from_screen_off=False):
        try:
            if path and os.path.exists(path):
                uri = f'file://{path}'
            else:
                uri = 'file://unavailable'
        except Exception:
            uri = 'file://unavailable'
        text = f'EMERGENCY! Photo: {uri}\\nLocation: location_unavailable'
        self._send_sms_all(text)
        self.set_status('Emergency SMS sent (if permissions allowed)')

    def _send_sms_all(self, message):
        if platform == 'android':
            try:
                sms_mgr = SmsManager.getDefault()
                for num in EMERGENCY_NUMBERS:
                    sms_mgr.sendTextMessage(num, None, message, None, None)
            except Exception as e:
                print('SMS error', e)
                self.set_status('SMS failed — check permissions')
        else:
            print('SIMULATED SMS to', EMERGENCY_NUMBERS, message)

    def on_test_sms(self, *args):
        self._send_sms_all('Be Safe test message from app')
        self.set_status('Test SMS sent')


class BeSafeApp(App):
    def build(self):
        return MainLayout()

if __name__ == '__main__':
    BeSafeApp().run()
