from ngramcropper import NgramCropper

image_folder = "words"
ngram_image_folder = "ngrams"
out_file = "ngram_list.ngl"
#cropper = NgramCropper(image_folder)
cropper = NgramCropper(image_folder, ngram_file=out_file)

# costruisci la lista di trigrammi
#cropper.build_ngram_list(3)
#cropper.build_ngram_list(2)

for box in cropper.all_ngrams:
    print(box)


# iterator
print("\nIl primo elemento è:")
print(cropper.next_box())
print("\nIl secondo elemento è:")
print(cropper.next_box())
print("\nIl terzo elemento è:")
print(cropper.next_box())

cropper.delete_current_box()

# save ngram file
cropper.save_ngramlist(out_file)

# save all ngram images
#cropper.build_ngram_images(ngram_image_folder)

print("-------------\nDone")