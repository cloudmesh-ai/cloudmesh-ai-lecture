import os
import numpy as np
import pandas as pd
from glob import glob
from PIL import Image

if not os.path.exists('data'):
    os.mkdir('data')


def random_array():
    if os.path.exists(os.path.join('data', 'random.hdf5')):
        return

    print("Create random data for array exercise")
    import h5py

    with h5py.File(os.path.join('data', 'random.hdf5'), 'w') as f:
        dset = f.create_dataset('/x', shape=(1000000000,), dtype='f4')
        for i in range(0, 1000000000, 1000000):
            dset[i: i + 1000000] = np.random.exponential(size=1000000)


def accounts_csvs(num_files, n, k):
    try:
        from accounts import account_entries, account_params
    except ImportError:
        print("Error: 'accounts' module not found. Please ensure it is in the python path.")
        return

    fn = os.path.join('data', 'accounts.%d.csv' % (num_files - 1))

    if os.path.exists(fn):
        return

    print("Create CSV accounts for dataframe exercise")

    args = account_params(k)

    for i in range(num_files):
        df = account_entries(n, *args)
        df.to_csv(os.path.join('data', 'accounts.%d.csv' % i),
                  index=False)


def accounts_json(num_files, n, k):
    try:
        from accounts import account_params, json_entries
    except ImportError:
        print("Error: 'accounts' module not found. Please ensure it is in the python path.")
        return

    import json
    import gzip
    fn = os.path.join('data', 'accounts.%02d.json.gz' % (num_files - 1))
    if os.path.exists(fn):
        return

    print("Create JSON accounts for bag exercise")

    args = account_params(k)

    for i in range(num_files):
        seq = json_entries(n, *args)
        fn = os.path.join('data', 'accounts.%02d.json.gz' % i)
        with gzip.open(fn, 'wb') as f:
            f.write(os.linesep.join(map(json.dumps, seq)).encode())


def create_weather(growth=3200):
    filenames = sorted(glob(os.path.join('data', 'weather-small', '*.hdf5')))

    if not os.path.exists(os.path.join('data', 'weather-big')):
        os.mkdir(os.path.join('data', 'weather-big'))

    if all(os.path.exists(fn.replace('small', 'big')) for fn in filenames):
        return

    import h5py

    for fn in filenames:
        with h5py.File(fn, mode='r') as f:
            x = f['/t2m'][:]
        
        # Replace scipy.misc.imresize with PIL.Image.resize
        # Convert numpy array to PIL Image, resize, then back to numpy array
        img = Image.fromarray(x)
        new_size = (img.width * growth, img.height * growth) # This is a simplified growth logic
        # Note: original imresize logic is complex, using a simple scale here
        # Since the original was likely using it for data augmentation/upscaling
        y = np.array(img.resize(new_size))

        out_fn = os.path.join('data', 'weather-big', os.path.split(fn)[-1])

        try:
            with h5py.File(out_fn, 'w') as f:
                f.create_dataset('/t2m', data=y, chunks=(500, 500))
        except Exception as e:
            print(f"Error creating {out_fn}: {e}")

if __name__ == '__main__':
    random_array()
    create_weather()
    accounts_csvs(3, 1000000, 500)
    accounts_json(50, 100000, 500)