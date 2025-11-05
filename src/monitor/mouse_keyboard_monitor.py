"""
Mouse und Keyboard Monitoring mit Windows Low-Level Hooks
"""

import win32api
import win32con
import win32gui
import win32ui
from typing import Optional, Callable, Dict
import threading
import time

from src.config.trigger_config import TriggerConfig
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MouseKeyboardMonitor:
    """Überwacht Mausklicks und Tastatureingaben mit Low-Level Hooks"""
    
    def __init__(self, mouse_callback: Optional[Callable] = None, keyboard_callback: Optional[Callable] = None, trigger_config: Optional[TriggerConfig] = None):
        """
        Initialisiert den Mouse/Keyboard Monitor
        
        Args:
            mouse_callback: Callback-Funktion die bei Mausklicks aufgerufen wird
            keyboard_callback: Callback-Funktion die bei Tastatureingaben aufgerufen wird
            trigger_config: Trigger-Konfiguration
        """
        self.mouse_callback = mouse_callback
        self.keyboard_callback = keyboard_callback
        self.monitoring = False
        self.monitor_thread = None
        
        # Lade Trigger-Konfiguration
        if trigger_config is None:
            trigger_config = TriggerConfig()
        self.trigger_config = trigger_config
        
        # Filter für relevante Events
        self.monitor_mouse_clicks = True
        self.monitor_keyboard = False  # Standard: nur Klicks, nicht Tastatureingaben
        self.ignored_keys = {win32con.VK_SHIFT, win32con.VK_CONTROL, win32con.VK_MENU}  # Modifier-Keys ignorieren
        
        # Tracking für Doppelklicks
        self.last_click_time = {}
        self.double_click_delay = trigger_config.double_click_delay  # Sekunden
        
        # Tracking für Tastatureingaben
        self.last_key_state = {}  # Speichert den letzten Zustand jeder Taste
        self.privacy_filter_enabled = True  # Filtert sensible Eingaben
        
        # Sensible Tasten die gefiltert werden sollen (Passwörter, PINs, etc.)
        self.sensitive_keys = {
            'PASSWORD', 'PIN', 'CVV', 'CVC', 'PASS', 'PWD'
        }
        
        # Mapping für Virtual Key Codes zu lesbaren Namen
        self.key_names = self._init_key_names()
    
    def start_monitoring(self):
        """Startet die Überwachung"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Beendet die Überwachung"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
    
    def _monitor_loop(self):
        """Hauptschleife für die Überwachung"""
        while self.monitoring:
            try:
                # Prüfe Mausklicks
                if self.monitor_mouse_clicks:
                    self._check_mouse_clicks()
                
                # Prüfe Tastatureingaben
                if self.monitor_keyboard:
                    self._check_keyboard()
                
                time.sleep(0.1)  # 10x pro Sekunde prüfen
            
            except Exception as e:
                logger.error(f"Fehler im Mouse/Keyboard Monitor-Loop: {e}", exc_info=True)
                time.sleep(0.5)
    
    def _check_mouse_clicks(self):
        """Prüft auf Mausklicks"""
        try:
            # Prüfe linke Maustaste
            if win32api.GetAsyncKeyState(win32con.VK_LBUTTON) & 0x8000:
                self._handle_mouse_click('left')
            
            # Prüfe rechte Maustaste
            if win32api.GetAsyncKeyState(win32con.VK_RBUTTON) & 0x8000:
                self._handle_mouse_click('right')
            
            # Prüfe mittlere Maustaste
            if win32api.GetAsyncKeyState(win32con.VK_MBUTTON) & 0x8000:
                self._handle_mouse_click('middle')
        
        except Exception as e:
            logger.error(f"Fehler beim Prüfen der Mausklicks: {e}", exc_info=True)
    
    def _handle_mouse_click(self, button: str):
        """
        Behandelt einen Mausklick
        
        Args:
            button: 'left', 'right', oder 'middle'
        """
        try:
            current_time = time.time()
            click_key = f"{button}"
            
            # Prüfe auf Doppelklick
            is_double_click = False
            if click_key in self.last_click_time:
                time_diff = current_time - self.last_click_time[click_key]
                if time_diff < self.double_click_delay:
                    is_double_click = True
            
            self.last_click_time[click_key] = current_time
            
            # Hole Mausposition und aktives Fenster
            pos = win32gui.GetCursorPos()
            hwnd = win32gui.WindowFromPoint(pos)
            
            if hwnd:
                window_info = self._get_window_info(hwnd)
                
                click_info = {
                    'button': button,
                    'position': {'x': pos[0], 'y': pos[1]},
                    'is_double_click': is_double_click,
                    'timestamp': time.time(),
                    'window_info': window_info
                }
                
                if self.mouse_callback:
                    self.mouse_callback(click_info)
        
        except Exception as e:
            logger.error(f"Fehler beim Behandeln des Mausklicks: {e}", exc_info=True)
    
    def _check_keyboard(self):
        """Prüft auf Tastatureingaben"""
        try:
            # Prüfe alle relevanten Tasten (A-Z, 0-9, Enter, Tab, Escape, etc.)
            for vk_code in range(0x08, 0xFE):  # Bereich der Virtual Key Codes
                if vk_code in self.ignored_keys:
                    continue
                
                # Prüfe ob Taste gedrückt wurde
                key_state = win32api.GetAsyncKeyState(vk_code)
                is_pressed = (key_state & 0x8000) != 0
                was_pressed = self.last_key_state.get(vk_code, False)
                
                # Neue Taste wurde gedrückt
                if is_pressed and not was_pressed:
                    self._handle_key_press(vk_code)
                
                # Aktualisiere Zustand
                self.last_key_state[vk_code] = is_pressed
        
        except Exception as e:
            logger.error(f"Fehler beim Prüfen der Tastatur: {e}", exc_info=True)
    
    def _handle_key_press(self, vk_code: int):
        """
        Behandelt eine Tastatureingabe
        
        Args:
            vk_code: Virtual Key Code
        """
        try:
            current_time = time.time()
            key_name = self.key_names.get(vk_code, f"VK_{vk_code:02X}")
            
            # Hole aktives Fenster
            hwnd = win32gui.GetForegroundWindow()
            window_info = None
            if hwnd:
                window_info = self._get_window_info(hwnd)
            
            # Prüfe ob Eingabe gefiltert werden soll
            should_filter = False
            if self.privacy_filter_enabled:
                window_title = window_info.get('title', '').upper() if window_info else ''
                for sensitive_term in self.sensitive_keys:
                    if sensitive_term in window_title:
                        should_filter = True
                        break
            
            key_info = {
                'key_code': vk_code,
                'key_name': key_name,
                'timestamp': current_time,
                'window_info': window_info,
                'filtered': should_filter
            }
            
            # Nur wenn nicht gefiltert, rufe Callback auf
            if self.keyboard_callback and not should_filter:
                self.keyboard_callback(key_info)
            elif should_filter:
                logger.debug(f"Tastatureingabe gefiltert (sensible Eingabe erkannt): {key_name}")
        
        except Exception as e:
            logger.error(f"Fehler beim Behandeln der Tastatureingabe: {e}", exc_info=True)
    
    def _init_key_names(self) -> Dict[int, str]:
        """
        Initialisiert Mapping von Virtual Key Codes zu lesbaren Namen
        
        Returns:
            Dictionary mit Key-Code zu Name Mapping
        """
        key_names = {}
        
        # Buchstaben A-Z
        for i in range(ord('A'), ord('Z') + 1):
            key_names[i] = chr(i)
        
        # Zahlen 0-9
        for i in range(ord('0'), ord('9') + 1):
            key_names[i] = chr(i)
        
        # Spezielle Tasten
        key_names[win32con.VK_RETURN] = 'Enter'
        key_names[win32con.VK_TAB] = 'Tab'
        key_names[win32con.VK_ESCAPE] = 'Escape'
        key_names[win32con.VK_SPACE] = 'Space'
        key_names[win32con.VK_BACK] = 'Backspace'
        key_names[win32con.VK_DELETE] = 'Delete'
        key_names[win32con.VK_INSERT] = 'Insert'
        key_names[win32con.VK_HOME] = 'Home'
        key_names[win32con.VK_END] = 'End'
        key_names[win32con.VK_PRIOR] = 'PageUp'
        key_names[win32con.VK_NEXT] = 'PageDown'
        key_names[win32con.VK_LEFT] = 'Left'
        key_names[win32con.VK_RIGHT] = 'Right'
        key_names[win32con.VK_UP] = 'Up'
        key_names[win32con.VK_DOWN] = 'Down'
        key_names[win32con.VK_F1] = 'F1'
        key_names[win32con.VK_F2] = 'F2'
        key_names[win32con.VK_F3] = 'F3'
        key_names[win32con.VK_F4] = 'F4'
        key_names[win32con.VK_F5] = 'F5'
        key_names[win32con.VK_F6] = 'F6'
        key_names[win32con.VK_F7] = 'F7'
        key_names[win32con.VK_F8] = 'F8'
        key_names[win32con.VK_F9] = 'F9'
        key_names[win32con.VK_F10] = 'F10'
        key_names[win32con.VK_F11] = 'F11'
        key_names[win32con.VK_F12] = 'F12'
        
        # Funktionstasten (nur einige wichtige)
        for i in range(13, 25):  # F1-F12 zusätzlich
            key_names[0x70 + i - 1] = f'F{i}'
        
        return key_names
    
    def _get_window_info(self, hwnd: int) -> Dict:
        """
        Extrahiert Informationen über ein Fenster
        
        Args:
            hwnd: Window Handle
            
        Returns:
            Dictionary mit Fenster-Informationen
        """
        try:
            title = win32gui.GetWindowText(hwnd)
            class_name = win32gui.GetClassName(hwnd)
            
            return {
                'hwnd': hwnd,
                'title': title,
                'class_name': class_name
            }
        
        except Exception:
            return {
                'hwnd': hwnd,
                'title': 'Unbekannt',
                'class_name': 'Unbekannt'
            }
    
    def set_monitor_keyboard(self, enable: bool):
        """
        Aktiviert/Deaktiviert Tastatur-Monitoring
        
        Args:
            enable: True um Tastatur-Monitoring zu aktivieren
        """
        self.monitor_keyboard = enable
    
    def set_monitor_mouse_clicks(self, enable: bool):
        """
        Aktiviert/Deaktiviert Mausklick-Monitoring
        
        Args:
            enable: True um Mausklick-Monitoring zu aktivieren
        """
        self.monitor_mouse_clicks = enable

