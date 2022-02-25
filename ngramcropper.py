import os, shutil
import math
from PIL import Image

OUT_FILE_EXTENSION = ".ngl"
NO_MORE_ITEMS = "No More Ngrams"

class NgramCropper():
    def __init__(self, word_folder_path, ngram_file=None):
        self.word_folder_path = word_folder_path
        self.all_ngrams = []
        self.current_index = None
        if ngram_file is not None:
            self.load_ngramlist(ngram_file)

    """
    Load a ngram list file
    It clears the previus ngram list.
    """
    def load_ngramlist(self, ngram_file):
        self.clear_ngram_list()
        with open(ngram_file, "r") as ngram_list_file:
                for line in ngram_list_file.readlines():
                    line = line.rstrip()
                    parts = line.split(",")
                    self.all_ngrams.append(NgramBox(parts[0],parts[1],parts[2],parts[3],parts[4],parts[5]))
        self.current_index = -1

    '''
    Define the N-grams of length ngram_size
    '''
    def build_ngram_list(self, ngram_size):
        for image_name in os.listdir(self.word_folder_path):
            image = Image.open(os.path.join(self.word_folder_path, image_name))
            
            word = image_name.split(".")[0].split("_")[-1]
            n_characters = len(word)
            
            char_width  = round(image.width / n_characters)
            ngram_width = math.ceil(char_width*ngram_size)

            for index_char in range(len(word)):
                if len(word) < ngram_size:
                    ngram_box = NgramBox(image_name, 0,0,image.width, image.height, word)
                    self.all_ngrams.append(ngram_box)
                    break
                
                if index_char+ngram_size <= len(word):
                    ngram = word[index_char:index_char+ngram_size]
                    start_x = index_char*char_width
                    end_x = (index_char*char_width)+ngram_width
                    if end_x > image.width:
                        end_x = image.width
                    ngram_box = NgramBox(image_name, start_x,0, end_x, image.height, ngram)
                    self.all_ngrams.append(ngram_box)
        self.all_ngrams.sort(key=lambda x: x.ngram_class)
        self.current_index = -1


    '''
    Update the current box in the ngram list
    '''
    def update_current_box(self, new_box):
        self.update_box(new_box, self.current_index)
    
    '''
    Update a box in the ngram list
    '''
    def update_box(self, new_box, index):
        self.all_ngrams[index] = new_box

    '''
    Get next ngram box
    '''
    def next_box(self):
        if self.current_index == None:
            return None
        elif self.current_index >= len(self.all_ngrams)-1:
            last_box = self.all_ngrams[-1]
            next_box = NgramBox(last_box.word_file, 0, 0, 0, 0, NO_MORE_ITEMS)       
            next_box.x1 = None
            
            self.current_index = len(self.all_ngrams)
        else:
            self.current_index += 1
            next_box = self.all_ngrams[self.current_index]
            
        return next_box

    '''
    Get previus ngram box
    '''
    def prev_box(self):
        if self.current_index == None:
            return None
        elif self.current_index -1 < 0:
            first_box = self.all_ngrams[0]
            next_box = NgramBox(first_box.word_file, 0, 0, 0, 0, NO_MORE_ITEMS)       
            next_box.x1 = None

            self.current_index = -1
        else:
            self.current_index -= 1
            next_box = self.all_ngrams[self.current_index]
        return next_box

    '''
    Get the index of current box
    '''
    def get_current_index(self):
        return self.current_index

    '''
    Get the number of ngrams
    '''
    def get_nuber_ngram(self):
        return len(self.all_ngrams)
    
    '''
    save all images of ngrams
    '''
    def build_ngram_images(self, ngrams_folder_path):
        self._clear_folder(ngrams_folder_path)
        for box in self.all_ngrams:
            extension = "." + box.word_file.split(".")[-1]
            word_image = Image.open(os.path.join(self.word_folder_path, box.word_file))
            ngram_image = word_image.crop((int(box.x1), int(box.y1), int(box.x2), int(box.y2)))

            ngram_index = 0
            ngram_file_path = os.path.join(ngrams_folder_path, str(ngram_index)+"_"+box.ngram_class + extension)
            while os.path.isfile(ngram_file_path):
                 ngram_index += 1
                 ngram_file_path = os.path.join(ngrams_folder_path, str(ngram_index)+"_"+box.ngram_class + extension)
            
            ngram_image.save(ngram_file_path)


    '''
    Clear the Ngram list
    '''
    def clear_ngram_list(self):
        self.all_ngrams = []
    
    '''
    Save Ngram list file
    '''
    def save_ngramlist(self, output_file_path):
        with open(output_file_path.split(".")[0]+OUT_FILE_EXTENSION, "w") as out_file:
            for ngram_box in self.all_ngrams:
                out_file.write(str(ngram_box)+"\n")
    
    '''
    Delete all content of th path folder
    '''
    def _clear_folder(self, path):
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

    def get_folder_path(self):
        return self.word_folder_path
    

'''
Calss for a single ngram.
it contains:
   - the name of original file
   - the coordinates of the boundinbox
   - the transcription of the ngram
'''
class NgramBox:
    def __init__(self, word_file, x1, y1, x2, y2, ngram_class):
        self.word_file = word_file
        self.x1 = int(x1)
        self.y1 = int(y1)
        self.x2 = int(x2)
        self.y2 = int(y2)
        self.ngram_class = ngram_class

    def __str__(self):
        return f"{self.word_file},{self.x1},{self.y1},{self.x2},{self.y2},{self.ngram_class}"