Participation to NaNoGenMo 2020 challenge.
See https://github.com/NaNoGenMo/2020/issues/17

## Installation of the writer
#### gpt-2 prerequisites
#### Build the folder structure and replace "francois" by your linux user.

/home/francois/gpt-2/src/watchdog_writer-runtime.py   
/home/francois/gpt-2/src/mymodules.py
/home/francois/gpt-2/models/              #Folder where to store the model, here the model is called writterrun06
/home/francois/gpt-2/writer/input_auto1/  #Folder to input the prompt file
/home/francois/gpt-2/writer/output_auto/  #Folder for gpt to provide the output  
/home/francois/gpt-2/writer/tmp/          #Folder for processing files

#### In watchdog_writer-runtime.py
Replace "francois" by your linux user or adjust paths to your preference.
Replace "writterrun06" by your gpt-2 fine-tuned model.

## Model training
I used the Max Wolf colab notebook at https://colab.research.google.com/drive/1VLG8e7YSEwypxU-noRNhsv5dW4NfTGce.
