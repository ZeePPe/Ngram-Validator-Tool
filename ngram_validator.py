from operator import mod
import os
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from ngramcropper import NgramCropper
from PIL import Image


IMAGE_FOLDER = "words"
NGRAM_FOLDER = "ngrams" 
OUT_FILE = "ngram_list.ngl"

"""
Class for selection Boxes
"""
class BoxSelector(Widget):
    position = NumericProperty(0)

"""
Class for word image
"""
class WordImage(Widget):
    image_source = StringProperty('')
    word_label = StringProperty('')
    ngram_label = StringProperty('')
    coordinate = StringProperty('')
    curr_ngram_index = StringProperty('0')



"""
In contains the basic grapghic for the background
"""
class Validator(Widget):
    
    # Action Bar
    btn_load_ngram = ObjectProperty(None)
    btn_save_ngram = ObjectProperty(None)
    btn_compute_ngram = ObjectProperty(None)

    box_selector_1 = ObjectProperty(None)
    box_selector_2 = ObjectProperty(None)
    ngram_image = ObjectProperty(None)

    num_of_ngrams = NumericProperty(0)
    
    def __init__(self, img_path, **kwargs):
        super(Validator, self).__init__(**kwargs)
        self.cropper =  NgramCropper(IMAGE_FOLDER, ngram_file=OUT_FILE)
        self.current_box = None

        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.ngram_image.word_label = "Premi SPAZIO per iniziare"
        self.box_selector_1.width=0
        self.box_selector_2.width=0
        self.btn_load_ngram.bind(state=self.callback_button_load_ngram)
        self.btn_save_ngram.bind(state=self.callback_button_save_ngram)
        self.btn_compute_ngram.bind(state=self.callback_button_compute_ngram)

        #self.show_popuo = PopupMessage()
        self.popupMessage = Popup(title="Wind", content=PopupMessage(), size_hint=(None,None), size=(400,100))
        self.pupop_ngram_computation = Popup(title="Ngram Computation", content=NgramComputPopup(self.cropper),size_hint=(None,None), size=(400, 400), auto_dismiss = True)
        
    
    '''
    Aggiorna l'interfaccia
    '''
    def update(self, box):
        self.current_box = box
        img_path = os.path.join(IMAGE_FOLDER, box.word_file)
        word_transcript = box.word_file.split(".")[0].split("_")[-1]
        img = Image.open(img_path)
        # BOX PAROLA
        self.ngram_image.x = self.center_x - round(img.width/2)
        self.ngram_image.y = self.center_y - round(img.height/2)
        self.ngram_image.width = img.width
        self.ngram_image.height = img.height
        self.ngram_image.image_source = img_path
        self.ngram_image.word_label = word_transcript
        self.ngram_image.ngram_label = box.ngram_class
        self.ngram_image.coordinate = f"(x1:{box.x1}, x2:{box.x2})"

        # Current Index
        self.ngram_image.curr_ngram_index = str(self.cropper.get_current_index()+1)

        #BOX DI SELEZIONE
        if box.x1 is not None:
            self.box_selector_1.height = box.y2 # right
            self.box_selector_2.height = box.y2 # left
            self.box_selector_1.y = self.center_y - round((img.height-box.y1)/2)
            self.box_selector_2.y = self.center_y - round((img.height-box.y1)/2)
            self.box_selector_1.width = - (img.width - box.x2)
            self.box_selector_2.width = box.x1
            self.box_selector_1.x = self.center_x + round(img.width/2) +1
            self.box_selector_2.x = self.center_x - round(img.width/2)



    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None
    
    '''
    Intercetta i tasti permuti dalla tastiera
    '''
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        #print(modifiers)
        #print(keycode)
        
        if len(modifiers) > 0 and modifiers[0] == 'ctrl'  and keycode[1] == 'right':  # Ctrl+up
            self.box_selector_2.width += 1
            self.current_box.x1 += 1
            self.ngram_image.coordinate = f"(x1:{self.current_box.x1}, x2:{self.current_box.x2})"
            print("ctr+r")
        elif len(modifiers) > 0 and modifiers[0] == 'ctrl'  and keycode[1] == 'left':
            self.box_selector_2.width -= 1
            self.current_box.x1 -= 1
            self.ngram_image.coordinate = f"(x1:{self.current_box.x1}, x2:{self.current_box.x2})"
            print("ctr+l")
        elif keycode[1] == 'right':
            self.box_selector_1.width += 1
            self.current_box.x2 += 1
            self.ngram_image.coordinate = f"(x1:{self.current_box.x1}, x2:{self.current_box.x2})"
            print("r")
        elif keycode[1] == 'left':
            self.box_selector_1.width -= 1
            self.current_box.x2 -= 1
            self.ngram_image.coordinate = f"(x1:{self.current_box.x1}, x2:{self.current_box.x2})"
            print("l")
        elif keycode[1] == 'spacebar':
            # next ngram
            print(self.current_box)
            if self.current_box is not None: 
                if self.current_box.x1 is not None:
                    self.cropper.update_current_box(self.current_box)
                    self.cropper.save_ngramlist(OUT_FILE)
            next_box = self.cropper.next_box()
            
            self.update(next_box)
        elif keycode[1] == 'backspace':
            # prev ngram
            print(self.current_box)
            if self.current_box is not None:
                if self.current_box.x1 is not None:
                    self.cropper.update_current_box(self.current_box)
                    self.cropper.save_ngramlist(OUT_FILE)
            prev_box = self.cropper.prev_box()
            self.update(prev_box)
        elif keycode[1] == 'delete':
            # delete ngram:
             if self.current_box is not None:
                if self.current_box.x1 is not None:
                    self.cropper.delete_current_box()
                    self.cropper.save_ngramlist(OUT_FILE)
                    self.update(self.cropper.get_current_box())
            
        return True 

    '''
    Bottoni Action bar
    '''
    def callback_button_load_ngram(self, button, click_mode):
        #print("click on", button.text)
        if click_mode == "down":
            # on click
            pass
        elif click_mode == "normal":
            # on release
            if self.cropper.get_nuber_ngram() > 0:
                if self.current_box is not None: 
                    if self.current_box.x1 is not None:
                        self.cropper.update_current_box(self.current_box)
                next_box = self.cropper.next_box()
                self.curr_ngram_inxex = self.cropper.get_current_index()+1
                self.num_of_ngrams = self.cropper.get_nuber_ngram()
                self.update(next_box)

    def callback_button_compute_ngram(self, button, click_mode):
        if click_mode == "down":
            pass
        elif click_mode == "normal":
            self.pupop_ngram_computation.open()
            #self.pupop_ngram_computation.dismiss()
            
    def callback_button_save_ngram(self, button, click_mode):
        if click_mode == "down":
            pass
        elif click_mode == "normal":
            self.cropper.build_ngram_images(NGRAM_FOLDER)
            
            self.popupMessage.title=f"Immagini Ngrammi create in '{NGRAM_FOLDER}'"
            self.popupMessage.open()
            pass



'''
Popup Message
'''
class PopupMessage(FloatLayout):
    def callback_ok_button(self):
        self.dismiss() # questa classe è solo il layout del popup, non posso richiamare dismiss che è di popup!

'''
Popup window for the ngram computation setting
'''
class NgramComputPopup(FloatLayout):
    def __init__(self, cropper):
        super(NgramComputPopup, self).__init__()
        self.cropper = cropper
        self.popupMessage = Popup(title="Wind", content=PopupMessage(), size_hint=(None,None), size=(400,100))
    
    def callback_ok_button(self):
        ngram_size = int(self.textinput_len_ngram.text)
        self.cropper.build_ngram_list(ngram_size)
        self.cropper.save_ngramlist(OUT_FILE)
        self.popupMessage.title=f"Ngrammi di lunghezza {ngram_size} calcolati!"
        self.popupMessage.open()
    
    def callback_delete_button(self):
        self.cropper.clear_ngram_list()
        self.cropper.save_ngramlist(OUT_FILE)
        self.popupMessage.title=f"Ngrammi cancellati!"
        self.popupMessage.open()
    

"""
Main Widjet
"""
class NgramValidatorApp(App):
    def build(self):
        main_gui = Validator("")
        return main_gui 



if __name__ == '__main__':
    NgramValidatorApp().run()

