"""
Element Discovery: Nutzt pywinauto um UI-Elemente zu finden
"""

from typing import List, Dict, Optional
from src.automation.automation_controller import AutomationController
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ElementDiscovery:
    """Nutzt pywinauto's descendants() und children() um UI-Elemente zu finden"""
    
    def __init__(self, automation_controller: AutomationController):
        """
        Initialisiert Element Discovery
        
        Args:
            automation_controller: Automation Controller Instanz
        """
        self.controller = automation_controller
    
    def discover_all_elements(self) -> List[Dict]:
        """
        Entdeckt alle UI-Elemente
        
        Returns:
            Liste von Element-Informationen
        """
        elements = []
        
        try:
            window = self.controller.window
            
            # Buttons
            buttons = self._discover_buttons(window)
            elements.extend(buttons)
            
            # Menü-Items
            menu_items = self._discover_menu_items(window)
            elements.extend(menu_items)
            
            # Links
            links = self._discover_links(window)
            elements.extend(links)
            
            # Eingabefelder
            input_fields = self._discover_input_fields(window)
            elements.extend(input_fields)
            
            # Checkboxen/Radio-Buttons
            checkboxes = self._discover_checkboxes(window)
            elements.extend(checkboxes)
            
            # Tabs
            tabs = self._discover_tabs(window)
            elements.extend(tabs)
            
            logger.info(f"{len(elements)} UI-Elemente entdeckt")
        
        except Exception as e:
            logger.error(f"Fehler bei Element-Discovery: {e}", exc_info=True)
        
        return elements
    
    def _discover_buttons(self, window) -> List[Dict]:
        """Entdeckt Buttons"""
        elements = []
        
        try:
            buttons = window.descendants(control_type="Button")
            for button in buttons:
                try:
                    rect = button.rectangle()
                    text = button.window_text()
                    
                    # Überspringe unsichtbare Buttons
                    if rect.width() == 0 or rect.height() == 0:
                        continue
                    
                    elements.append({
                        'type': 'button',
                        'text': text,
                        'x': (rect.left + rect.right) // 2,
                        'y': (rect.top + rect.bottom) // 2,
                        'bbox': {
                            'left': rect.left,
                            'top': rect.top,
                            'right': rect.right,
                            'bottom': rect.bottom,
                            'width': rect.width(),
                            'height': rect.height()
                        },
                        'visible': button.is_visible(),
                        'enabled': button.is_enabled()
                    })
                except Exception:
                    continue
        
        except Exception as e:
            logger.debug(f"Fehler beim Entdecken von Buttons: {e}")
        
        return elements
    
    def _discover_menu_items(self, window) -> List[Dict]:
        """Entdeckt Menü-Items"""
        elements = []
        
        try:
            menu_items = window.descendants(control_type="MenuItem")
            for item in menu_items:
                try:
                    rect = item.rectangle()
                    text = item.window_text()
                    
                    if rect.width() == 0 or rect.height() == 0:
                        continue
                    
                    elements.append({
                        'type': 'menu_item',
                        'text': text,
                        'x': (rect.left + rect.right) // 2,
                        'y': (rect.top + rect.bottom) // 2,
                        'bbox': {
                            'left': rect.left,
                            'top': rect.top,
                            'right': rect.right,
                            'bottom': rect.bottom,
                            'width': rect.width(),
                            'height': rect.height()
                        },
                        'visible': item.is_visible(),
                        'enabled': item.is_enabled()
                    })
                except Exception:
                    continue
        
        except Exception as e:
            logger.debug(f"Fehler beim Entdecken von Menü-Items: {e}")
        
        return elements
    
    def _discover_links(self, window) -> List[Dict]:
        """Entdeckt Links (Hyperlinks)"""
        elements = []
        
        try:
            # Links sind oft als Text-Controls mit Hyperlink-Funktion
            links = window.descendants(control_type="Hyperlink")
            for link in links:
                try:
                    rect = link.rectangle()
                    text = link.window_text()
                    
                    if rect.width() == 0 or rect.height() == 0:
                        continue
                    
                    elements.append({
                        'type': 'link',
                        'text': text,
                        'x': (rect.left + rect.right) // 2,
                        'y': (rect.top + rect.bottom) // 2,
                        'bbox': {
                            'left': rect.left,
                            'top': rect.top,
                            'right': rect.right,
                            'bottom': rect.bottom,
                            'width': rect.width(),
                            'height': rect.height()
                        },
                        'visible': link.is_visible(),
                        'enabled': link.is_enabled()
                    })
                except Exception:
                    continue
        
        except Exception as e:
            logger.debug(f"Fehler beim Entdecken von Links: {e}")
        
        return elements
    
    def _discover_input_fields(self, window) -> List[Dict]:
        """Entdeckt Eingabefelder"""
        elements = []
        
        try:
            # Edit-Controls sind Eingabefelder
            edit_controls = window.descendants(control_type="Edit")
            for edit in edit_controls:
                try:
                    rect = edit.rectangle()
                    
                    if rect.width() == 0 or rect.height() == 0:
                        continue
                    
                    elements.append({
                        'type': 'input_field',
                        'text': edit.window_text() or '',
                        'x': (rect.left + rect.right) // 2,
                        'y': (rect.top + rect.bottom) // 2,
                        'bbox': {
                            'left': rect.left,
                            'top': rect.top,
                            'right': rect.right,
                            'bottom': rect.bottom,
                            'width': rect.width(),
                            'height': rect.height()
                        },
                        'visible': edit.is_visible(),
                        'enabled': edit.is_enabled()
                    })
                except Exception:
                    continue
        
        except Exception as e:
            logger.debug(f"Fehler beim Entdecken von Eingabefeldern: {e}")
        
        return elements
    
    def _discover_checkboxes(self, window) -> List[Dict]:
        """Entdeckt Checkboxen und Radio-Buttons"""
        elements = []
        
        try:
            # Checkboxen
            checkboxes = window.descendants(control_type="CheckBox")
            for checkbox in checkboxes:
                try:
                    rect = checkbox.rectangle()
                    text = checkbox.window_text()
                    
                    if rect.width() == 0 or rect.height() == 0:
                        continue
                    
                    elements.append({
                        'type': 'checkbox',
                        'text': text,
                        'x': (rect.left + rect.right) // 2,
                        'y': (rect.top + rect.bottom) // 2,
                        'bbox': {
                            'left': rect.left,
                            'top': rect.top,
                            'right': rect.right,
                            'bottom': rect.bottom,
                            'width': rect.width(),
                            'height': rect.height()
                        },
                        'visible': checkbox.is_visible(),
                        'enabled': checkbox.is_enabled(),
                        'checked': checkbox.get_toggle_state() if hasattr(checkbox, 'get_toggle_state') else False
                    })
                except Exception:
                    continue
            
            # Radio-Buttons
            radio_buttons = window.descendants(control_type="RadioButton")
            for radio in radio_buttons:
                try:
                    rect = radio.rectangle()
                    text = radio.window_text()
                    
                    if rect.width() == 0 or rect.height() == 0:
                        continue
                    
                    elements.append({
                        'type': 'radio',
                        'text': text,
                        'x': (rect.left + rect.right) // 2,
                        'y': (rect.top + rect.bottom) // 2,
                        'bbox': {
                            'left': rect.left,
                            'top': rect.top,
                            'right': rect.right,
                            'bottom': rect.bottom,
                            'width': rect.width(),
                            'height': rect.height()
                        },
                        'visible': radio.is_visible(),
                        'enabled': radio.is_enabled(),
                        'checked': radio.is_selected() if hasattr(radio, 'is_selected') else False
                    })
                except Exception:
                    continue
        
        except Exception as e:
            logger.debug(f"Fehler beim Entdecken von Checkboxen/Radio-Buttons: {e}")
        
        return elements
    
    def _discover_tabs(self, window) -> List[Dict]:
        """Entdeckt Tabs"""
        elements = []
        
        try:
            tabs = window.descendants(control_type="Tab")
            for tab in tabs:
                try:
                    # Tab-Items
                    tab_items = tab.children()
                    for item in tab_items:
                        try:
                            rect = item.rectangle()
                            text = item.window_text()
                            
                            if rect.width() == 0 or rect.height() == 0:
                                continue
                            
                            elements.append({
                                'type': 'tab',
                                'text': text,
                                'x': (rect.left + rect.right) // 2,
                                'y': (rect.top + rect.bottom) // 2,
                                'bbox': {
                                    'left': rect.left,
                                    'top': rect.top,
                                    'right': rect.right,
                                    'bottom': rect.bottom,
                                    'width': rect.width(),
                                    'height': rect.height()
                                },
                                'visible': item.is_visible(),
                                'enabled': item.is_enabled()
                            })
                        except Exception:
                            continue
                except Exception:
                    continue
        
        except Exception as e:
            logger.debug(f"Fehler beim Entdecken von Tabs: {e}")
        
        return elements

