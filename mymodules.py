import os
import logging
import numpy as np
import tensorflow as tf
import model, sample, encoder
import json
import datetime

#Disable warning
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

#Initiate logging
logger = logging.getLogger("gpt2-experiments")
logger.setLevel(logging.INFO)
logging.basicConfig(
    format="%(asctime)s — %(levelname)s — %(name)s — %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
    level=logging.INFO,
)
    

#For watchdog_writer-runtime.py
def single_interact_model_4(
    #output_dir,
    #output_file,
    models_dir,
    model_name,
    seedinput,
    outputlength,
    temperature,
    top_k,
    top_p,
):
        
        seed=None
        nsamples=1 #x possible 
        batch_size=1
        
        enc = encoder.get_encoder(model_name)
        hparams = model.default_hparams()
        with open(os.path.join(models_dir, model_name, 'hparams.json')) as f:
            hparams.override_from_dict(json.load(f))
        if outputlength is None:
            outputlength = hparams.n_ctx // 2
        elif outputlength > hparams.n_ctx:
            raise ValueError("Can't get samples longer than window size: %s" % hparams.n_ctx)

        with tf.Session(graph=tf.Graph()) as sess:
            context = tf.placeholder(tf.int32, [batch_size, None])
            np.random.seed(seed)
            tf.set_random_seed(seed)
            output = sample.sample_sequence(
                hparams=hparams, length=outputlength,
                context=context,
                batch_size=batch_size,
                temperature=temperature, top_k=top_k, top_p=top_p
            )

            saver = tf.train.Saver()
            ckpt = tf.train.latest_checkpoint(os.path.join(models_dir, model_name))
            saver.restore(sess, ckpt)

            context_tokens = enc.encode(seedinput)
            generated = 0
        
            for _ in range(nsamples // batch_size):
                out = sess.run(output, feed_dict={
                    context: [context_tokens for _ in range(batch_size)]
                
                })[:, len(context_tokens):]
                for i in range(batch_size):
                    generated += 1
                    output = enc.decode(out[i])

            print("-" * 80)
        return output

