import os
import subprocess
import tempfile

EDITOR = os.environ.get('EDITOR','nano')


def editor_input():
    with tempfile.NamedTemporaryFile('r', suffix=".tmp") as tf:
      subprocess.call([EDITOR, tf.name])
      return tf.read()
