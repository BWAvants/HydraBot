#  Database functionality for HydraBot

import os
from time import time, ctime, localtime, strftime
from collections import OrderedDict
import json
import gzip
import tarfile
from PyQt5.QtGui import QImage
from PyQt5.QtCore import QByteArray, QBuffer, QIODevice
from io import BytesIO


def obj_to_dict(obj):
    obj_dict = OrderedDict(obj.__dict__)
    for key in obj_dict.keys():
        if 'parent' in key or '__' in key:
            del obj_dict[key]
        if 'image' in key and 'path' not in key:
            del obj_dict[key]
        if 'events' in key or 'colonies' in key or 'animals' in key:
            child_obj_dicts = []
            for child in obj_dict[key]:
                child_obj_dicts.append(obj_to_dict(child))
            obj_dict[key] = child_obj_dicts
    obj_dict.update({
        '__class__': obj.__class__.__name__,
        '__module__': obj.__module__
    })
    return obj_dict


def dict_to_object(obj_dict, parent=None):
    if '__class__' in obj_dict:
        class_name = obj_dict.pop('__class__')
        module_name = obj_dict.pop('__module__')
        module = __import__(module_name)
        class_ = getattr(module, class_name)
        if parent:
            obj = class_(parent, **obj_dict)
        else:
            obj = class_(**obj_dict)
    else:
        obj = obj_dict
    return obj


def get_date_string(obj):
    if obj.__class__ == 'str':
        return ctime(obj)
    try:
        if 'founded' in obj.__dict__:
            return strftime('%Y-%m-%d %H:%M', localtime(obj.founded))
            # return ctime(obj.founded)
        if 'created' in obj.__dict__:
            return strftime('%Y-%m-%d %H:%M', localtime(obj.created))
            # return ctime(obj.created)
        if 'happened' in obj.__dict__:
            return strftime('%Y-%m-%d %H:%M', localtime(obj.happened))
            # return ctime(obj.happened)
    except:
        return ''


def check_path(base_path: str = '', possible_path: str = ''):
    if os.path.isdir(os.path.join(base_path, possible_path)) is True:
        return os.path.join(base_path, possible_path)
    if os.path.isdir(possible_path) is True:
        return possible_path
    return None


def plate_manifest(stock):
    manifest = {}
    for animal in stock:
        for colony in animal:
            try:
                plate, well = colony.location.split(':')
            except:
                continue
            if plate not in manifest:
                manifest.update({plate: {well: (animal.name, colony.ID, colony)}})
            else:
                manifest[plate].update({well: (animal.name, colony.ID, colony)})
    return manifest


def qimg_to_bytesio(qimg):
    byte_array = QByteArray()
    buffer = QBuffer(byte_array)
    buffer.open(QIODevice.WriteOnly)
    qimg.save(buffer, 'PNG')
    b = BytesIO(buffer.data())
    buffer.close()
    total_bytes = b.tell()
    b.seek(0)
    return b, total_bytes


def load(location: str, load_images=False, save_decompressed=False, decompress_to=None):
    hydb = None
    if os.path.isfile(location) is True:
        if location.endswith('.tar.gz'):
            with tarfile.open(location) as tf:
                hydb = json.load(tf.extractfile(tf.next()), object_hook=dict_to_object,
                                 object_pairs_hook=OrderedDict)
                if save_decompressed is True:
                    if decompress_to is None:
                        tf.extractall(os.path.dirname(location))
                    elif os.path.isdir(decompress_to) is True:
                        tf.extractall(decompress_to)
                    else:
                        print('invalid decompression path')
                if load_images is True:
                    names = tf.getnames()
                    if len(names) > 1:
                        members = tf.getmembers()
                        images = dict()
                        for i in range(1, len(names)):
                            images[names[i]] = tf.extractfile(members[i])
                        hydb.load_images(files=images)
                    else:
                        hydb.load_images()
        else:
            if location.endswith('.hyd') is True:
                with open(location, 'w') as f:
                    hydb = json.load(f, object_hook=dict_to_object, object_pairs_hook=OrderedDict)

            elif location.endswith('gz'):
                with gzip.open(location) as f:
                    hydb = json.load(f, object_hook=dict_to_object, object_pairs_hook=OrderedDict)
            if load_images is True:
                    hydb.load_images()
    return hydb


class Stock:

    class Animal:

        class Colony:

            class Event:

                def __init__(self, stock, animal, colony, event='Feeding', happened=time(), location_before=None,
                             location_after=None, population_before=0, population_after=0,
                             image_before=None, image_after=None, **kwargs):
                    self.stock = stock
                    self.animal = animal
                    self.colony = colony
                    self.parent = colony
                    self.relative_path = ''
                    self.event = event  # Specify what happened: Feeding, Moving, Merging, etc...
                    self.happened = happened
                    self.location_before = location_before
                    self.location_after = location_after
                    self.population_before = population_before
                    self.population_after = population_after
                    self.image_before = image_before
                    self.image_before_path = None
                    self.image_after = image_after
                    self.image_after_path = None
                    self.icon_image = None
                    self.icon_image_path = None
                    self.notes = OrderedDict()
                    self.name = event + '~' + strftime('%Y-%m-%d %H:%M', localtime(happened))
                    for param, val in kwargs.items():
                        setattr(self, param, val)

                def __repr__(self):
                    return self.name

                def __str__(self):
                    return self.name

                def info(self):
                    return '%s, colony %d, %d' % (self.event, self.parent.ID, self.happened)

                def add_note(self, note: str, timestamp=time()):
                    self.notes[str(timestamp)] = note

                def append_note(self, note: str, timestamp: str):
                    if timestamp in self.notes:
                        original_note = self.notes[timestamp]
                        self.notes[timestamp] = original_note + '\t\n' + note
                        return True
                    else:
                        return False

                def get_note(self, timestamp: str):
                    if timestamp in self.notes:
                        return self.notes[timestamp]
                    else:
                        return None

                def overwrite_note(self, note: str, timestamp: str):
                    if timestamp in self.notes:
                        self.notes[timestamp] = note
                        return True
                    else:
                        return False

                def del_note(self, timestamp: str):
                    if timestamp in self.notes:
                        del self.notes[timestamp]
                        return True
                    else:
                        return False

                def set_population_after(self, population):
                    self.populationAfter = population
                    self.parent.update_population()

                def save_images(self, location: str, backup=False):
                    if self.imageBefore is None and self.imageAfter is None:
                        return
                    try:
                        os.makedirs(location, exist_ok=True)
                    except OSError:
                        raise
                    eventname = strftime('%Y%m%d%H%M%S', localtime(self.happened)) + '-' + self.event
                    if self.imageBefore:
                        filename = eventname + '_before.png'
                        fullname = os.join(location, filename)
                        if backup is True and os.path.isfile(fullname) is True:
                            os.rename(fullname, fullname + '.old.png')
                        if self.imageBefore.save(fullname) is True:
                            self.imageBefore_path = fullname
                        else:
                            print('imageBefore save failed')
                    if self.imageAfter:
                        filename = eventname + '_after.png'
                        fullname = os.join(location, filename)
                        if backup is True and os.path.isfile(fullname) is True:
                            os.rename(fullname, fullname + '.old.png')
                        if self.imageAfter.save(fullname) is True:
                            self.imageAfter_path = fullname
                        else:
                            print('imageAfter save failed')

                def load_images(self):
                    images_loaded = 0
                    if self.imageBefore_path is not None and os.path.isfile(self.imageBefore_path):
                        qimg = QImage(self.imageBefore_path)
                        if qimg.isNull() is False:
                            self.imageBefore = qimg
                        images_loaded += 1
                    if self.imageAfter_path is not None and os.path.isfile(self.imageAfter_path):
                        qimg = QImage(self.imageAfter_path)
                        if qimg.isNull() is False:
                            self.imageAfter = qimg
                        images_loaded += 1
                    return images_loaded

            class _event_iter:
                def __init__(self, events, attrib=None):
                    self.events = events
                    self.attrib = attrib
                    self.cur = 0

                def __iter__(self):
                    return self

                def __next__(self):
                    i = self.cur
                    if i >= len(self.events):
                        raise StopIteration
                    self.cur += 1
                    if self.attrib is None:
                        return self.events[i]
                    else:
                        return getattr(self.events, self.attrib)

            def __init__(self, stock, animal, identifier=0, founded=time(), **kwargs):
                self.stock = stock
                self.animal = animal
                self.parent = animal
                self.latest_event = None
                self.relative_path = ''
                self.ID = identifier
                self.name = str(self.ID)
                self.founded = founded
                self.plate = 'plateID'
                self.well = 'A1'
                self.population = 0
                self.stereotype_image = None
                self.stereotype_image_path = None
                self.icon_image = None
                self.icon_image_path = None
                self.abolished = None
                self.events = []
                self.notes = OrderedDict()
                for param, val in kwargs.items():
                    if 'events' in param:
                        for event in kwargs[param]:
                            self.events.append(dict_to_object(event, self))
                    else:
                        setattr(self, param, val)
                self.location = self.plate + ':' + self.well

            def __iter__(self):
                return Stock.Animal.Colony._event_iter(self.events)

            def __repr__(self):
                return self.name

            def __str__(self):
                return self.name

            def info(self):
                return 'Colony %d, %s, %s:%s, population %d' % (
                    self.ID, self.animal, self.plate, self.well, self.population)

            def add_event(self, event: str = 'Feeding', **kwargs):
                #  Useful kwargs are as follows, but Events will accept all passed kwargs:
                #  feeding, timestamp, locationBefore, locationAfter,
                #  populationBefore, populationAfter, imageBefore, imageAfter
                newEvent = Stock.Animal.Colony.Event(self.stock, self.animal, self, event=event, **kwargs)
                self.events.append(newEvent)
                if self.latest_event is None:
                    self.latest_event = newEvent
                else:
                    latest = newEvent
                    for event in self:
                        if latest.happened < event.happened:
                            latest = event
                    self.latest_event = latest
                return newEvent

            def del_event(self, event):
                try:
                    self.events.remove(event)
                    return True
                except ValueError:
                    print('Attempted to remove an Event that did not exist: %s - %d' % self.parent.name, self.ID)
                    return False

            def abolish(self, timestamp=time()):
                self.abolished = timestamp

            def is_alive(self):
                return self.abolished is None

            def update_population(self):
                if self.latest_event is None:
                    return 0
                self.population = self.latest_event.population_after
                return self.population

            def add_note(self, note: str, timestamp=time()):
                self.notes[str(timestamp)] = note

            def append_note(self, note: str, timestamp: str):
                if timestamp in self.notes:
                    original_note = self.notes[timestamp]
                    self.notes[timestamp] = original_note + '\t\n' + note
                    return True
                else:
                    return False

            def get_note(self, timestamp: str):
                if timestamp in self.notes:
                    return self.notes[timestamp]
                else:
                    return None

            def overwrite_note(self, note: str, timestamp: str):
                if timestamp in self.notes:
                    self.notes[timestamp] = note
                    return True
                else:
                    return False

            def del_note(self, timestamp: str):
                if timestamp in self.notes:
                    del self.notes[timestamp]
                    return True
                else:
                    return False

            def save_images(self, location: str, backup=False):
                if self.stereotype_image is None and self.icon_image is None:
                    return
                try:
                    os.makedirs(location, exist_ok=True)
                except OSError:
                    raise
                if self.stereotype_image:
                    fullname = os.join(location, self.name + '_stereotype.png')
                    if backup is True and os.path.isfile(fullname) is True:
                        os.rename(fullname, fullname + '.old.png')
                    if self.stereotype_image.save(fullname) is True:
                        self.stereotype_image_path = fullname
                    else:
                        print('stereotype_image save failed')
                if self.icon_image:
                    fullname = os.join(location, self.name + '_icon.png')
                    if backup is True and os.path.isfile(fullname) is True:
                        os.rename(fullname, fullname + '.old.png')
                    if self.icon_image.save(fullname) is True:
                        self.icon_image_path = fullname
                    else:
                        print('icon_image save failed')

            def load_images(self):
                images_loaded = 0
                if self.stereotype_image_path is not None and os.path.isfile(self.stereotype_image_path):
                    qimg = QImage(self.stereotype_image_path)
                    if qimg.isNull() is False:
                        self.stereotype_image = qimg
                    images_loaded += 1
                if self.icon_image_path is not None and os.path.isfile(self.icon_image_path):
                    qimg = QImage(self.icon_image_path)
                    if qimg.isNull() is False:
                        self.icon_image = qimg
                    images_loaded += 1
                return images_loaded

        class _colony_iter:
            def __init__(self, colonies, attrib=None):
                self.colonies = colonies
                self.attrib = attrib
                self.cur = 0

            def __iter__(self):
                return self

            def __next__(self):
                i = self.cur
                if i >= len(self.colonies):
                    raise StopIteration
                self.cur += 1
                if self.attrib is None:
                    return self.colonies[i]
                else:
                    return getattr(self.colonies[i], self.attrib)

        def __init__(self, stock, name='Hydra Vulgaris', **kwargs):
            self.stock = stock
            self.name = name
            self.relative_path = ''
            self.created = time()
            self.max_population_density = 10
            self.population = 0
            self.stereotype_image = None
            self.stereotype_image_path = None
            self.icon_image = None
            self.icon_image_path = None
            self.colonies = []
            self.nextID = 1
            self.notes = OrderedDict()
            for param, val in kwargs.items():
                if 'colonies' in param:
                    for colony in kwargs[param]:
                        self.colonies.append(dict_to_object(colony))
                else:
                    setattr(self, param, val)

        def __iter__(self):
            return Stock.Animal._colony_iter(self.colonies)

        def __repr__(self):
            return self.name

        def __str__(self):
            return self.name

        def names(self):
            return Stock.Animal._colony_iter(self.colonies, attrib='name')

        def info(self):
            return '%s, colonies %d, population %d' % (self.name, len(self.colonies), self.population)

        def add_colony(self, **kwargs):
            current_IDs = []
            for colony in self:
                current_IDs.append(colony.ID)
            while self.nextID in current_IDs:
                self.nextID += 1
            colony = Stock.Animal.Colony(self.stock, self, identifier=self.nextID, **kwargs)
            self.colonies.append(colony)
            self.nextID += 1
            return colony

        def add_note(self, note: str, timestamp=time()):
            self.notes[str(timestamp)] = note

        def append_note(self, note: str, timestamp: str):
            if timestamp in self.notes:
                original_note = self.notes[timestamp]
                self.notes[timestamp] = original_note + '\t\n' + note
                return True
            else:
                return False

        def get_note(self, timestamp: str):
            if timestamp in self.notes:
                return self.notes[timestamp]
            else:
                return None

        def overwrite_note(self, note: str, timestamp: str):
            if timestamp in self.notes:
                self.notes[timestamp] = note
                return True
            else:
                return False

        def del_note(self, timestamp: str):
            if timestamp in self.notes:
                del self.notes[timestamp]
                return True
            else:
                return False

        def update_population(self):
            total = 0
            for colony in self:
                if colony.is_alive():
                    total += colony.update_population()
            self.population = total
            return total

        def save_images(self, location: str = '', base_path='', backup=False):
            if self.stereotype_image is None and self.icon_image is None:
                return
            if len(location) < 1:
                location = self.relative_path
            full_path = os.path.join(base_path, location)
            try:
                os.makedirs(full_path, exist_ok=True)
            except OSError:
                raise
            if self.stereotype_image:
                fullname = os.path.join(full_path, self.name + '_stereotype.png')
                if backup is True and os.path.isfile(fullname) is True:
                    os.rename(fullname, fullname + '.old.png')
                if self.stereotype_image.save(fullname) is True:
                    self.stereotype_image_path = os.path.join(location, self.name + '_stereotype.png')
                else:
                    print('stereotype_image save failed')
            if self.icon_image:
                fullname = os.path.join(base_path, location, self.name + '_icon.png')
                if backup is True and os.path.isfile(fullname) is True:
                    os.rename(fullname, fullname + '.old.png')
                if self.icon_image.save(fullname) is True:
                    self.icon_image_path = os.path.join(location, self.name + '_icon.png')
                else:
                    print('icon_image save failed')

        def load_images(self, base_path='', files=None, recursive=False):
            if recursive is True:
                next_path = os.path.join(base_path, self.name)
                for colony in self:
                    colony.load_images(base_path=next_path, files=files, recursive=True)
            images_loaded = 0
            if files is None:
                if self.stereotype_image_path is not None:
                    file_name = os.path.join(base_path, self.stereotype_image_path)
                    if os.path.isfile(file_name):
                        qimg = QImage(file_name)
                        if qimg.isNull() is False:
                            self.stereotype_image = qimg
                        images_loaded += 1
                if self.icon_image_path is not None:
                    file_name = os.path.join(base_path, self.icon_image_path)
                    if os.path.isfile(file_name):
                        qimg = QImage(file_name)
                        if qimg.isNull() is False:
                            self.icon_image = qimg
                        images_loaded += 1
                return images_loaded
            else:
                pass

    class _animal_iter:
        def __init__(self, animals, attrib=None):
            self.animals = animals
            self.attrib = attrib
            self.cur = 0

        def __iter__(self):
            return self

        def __next__(self):
            i = self.cur
            if i >= len(self.animals):
                raise StopIteration
            self.cur += 1
            if self.attrib is None:
                return self.animals[i]
            else:
                return getattr(self.animals[i], self.attrib)

    def __init__(self, name='HydraStock', **kwargs):
        self.name = name
        self.founded = time()
        self.notes = OrderedDict()
        self.animals = []
        self.population = 0
        self.icon_image = None
        self.icon_image_path = None
        self.stereotype_image = None
        self.stereotype_image_path = None
        self.parent = None
        self.base_path = os.getcwd()
        for param, val in kwargs.items():
            if 'animals' in param:
                for animal in kwargs[param]:
                    self.animals.append(dict_to_object(animal))
            else:
                setattr(self, param, val)

    def __iter__(self):
        return Stock._animal_iter(self.animals)

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    def info(self):
        return '%s Stock, Animals %d, population %d' % (self.name, len(self.animals), self.population)

    def names(self):
        return Stock._animal_iter(self.animals, attrib='name')

    def add_animal(self, name='Hydra Vulgaris', **kwargs):
        if name in self.names():
            return
        kwargs.update({'parent': self})
        animal = Stock.Animal(self, name=name, **kwargs)
        self.animals.append(animal)
        return animal

    def del_animal(self, name):
        for animal in self:
            if name == animal.name:
                self.animals.remove(animal)
                return True
        return False

    def update_population(self):
        new_pop = 0
        for animal in self:
            new_pop += animal.update_population()
        self.population = new_pop
        return new_pop

    def add_note(self, note: str, timestamp=time()):
        self.notes[str(timestamp)] = note

    def append_note(self, note: str, timestamp: str):
        if timestamp in self.notes:
            original_note = self.notes[timestamp]
            self.notes[timestamp] = original_note + '\t\n' + note
            return True
        else:
            return False

    def get_note(self, timestamp: str):
        if timestamp in self.notes:
            return self.notes[timestamp]
        else:
            return None

    def overwrite_note(self, note: str, timestamp: str):
        if timestamp in self.notes:
            self.notes[timestamp] = note
            return True
        else:
            return False

    def del_note(self, timestamp: str):
        if timestamp in self.notes:
            del self.notes[timestamp]
            return True
        else:
            return False

    def save(self, location: str, backup=True, compress=False, include_images=False):
        try:
            os.makedirs(location, exist_ok=True)
        except OSError:
            raise
        fullname = os.path.join(location, self.name + '.hyd')
        self.update_population()
        if compress is False:
            if backup is True and os.path.isfile(fullname) is True:
                    os.rename(fullname, fullname + '.old')
            # obj_dict = obj_to_dict(self)
            with open(fullname, 'w') as f:
                json.dump(self, f, default=obj_to_dict)
                # json.dump(obj_dict, f)
            if include_images is True:
                stock_path = os.path.join(location, self.name)
                os.makedirs(stock_path, exist_ok=True)
                for animal in self:
                    animal_path = os.path.join(stock_path, animal.name)
                    os.makedirs(animal_path, exist_ok=True)
                    animal.save_images(animal_path, backup=backup)
                    for colony in animal:
                        colony_path = os.path.join(animal_path, colony.ID)
                        os.makedirs(colony_path, exist_ok=True)
                        colony.save_images(colony_path, backup=backup)
                        for event in colony:
                            event.save_images(colony_path, backup=backup)
        else:
            db_str = json.dumps(self, default=obj_to_dict).encode('utf-8')
            if include_images is False:
                fullname = fullname + '.gz'
                if backup is True and os.path.isfile(fullname) is True:
                    os.rename(fullname, fullname + '.old')
                with gzip.open(fullname, 'wb') as f:
                    f.write(db_str)
            else:
                fullname = fullname + '.tar.gz'
                if backup is True and os.path.isfile(fullname) is True:
                    os.rename(fullname, fullname + '.old')
                with tarfile.open(name=fullname, mode='x:gz') as tf:
                    # Make TarInfo for each "file", add with tf.addfile(info, fileobj)
                    info = tarfile.TarInfo(name=self.name + '.hyd')
                    info.size = len(db_str)
                    tf.addfile(tarinfo=info, fileobj=db_str)
                    total_images = 0
                    for animal in self:
                        if animal.stereotype_image is not None:
                            total_images += 1
                        if animal.icon_image is not None:
                            total_images += 1
                        for colony in animal:
                            if colony.stereotype_image is not None:
                                total_images += 1
                            if colony.icon_image is not None:
                                total_images += 1
                            for event in colony:
                                if event.image_before is not None:
                                    total_images += 1
                                if event.image_after is not None:
                                    total_images += 1
                    print('Saving %d images' % total_images)
                    stock_path = self.name
                    for animal in self:
                        animal_path = os.path.join(stock_path, animal.name)
                        if animal.stereotype_image is not None:
                            stereotype_image, total_bytes = qimg_to_bytesio(animal.stereotype_image)
                            info = tarfile.TarInfo(name=os.path.join(animal_path, 'stereotype_image.png'))
                            info.size = total_bytes
                            tf.addfile(tarinfo=info, fileobj=stereotype_image)
                        if animal.icon_image is not None:
                            icon_image, total_bytes = qimg_to_bytesio(animal.icon_image)
                            info = tarfile.TarInfo(name=os.path.join(animal_path, 'icon_image.png'))
                            info.size = total_bytes
                            tf.addfile(tarinfo=info, fileobj=icon_image)
                        for colony in animal:
                            colony_path = os.path.join(animal_path, colony.ID)
                            if colony.stereotype_image is not None:
                                stereotype_image, total_bytes = qimg_to_bytesio(colony.stereotype_image)
                                info = tarfile.TarInfo(name=os.path.join(colony_path, 'stereotype_image.png'))
                                info.size = total_bytes
                                tf.addfile(tarinfo=info, fileobj=stereotype_image)
                            if colony.icon_image is not None:
                                icon_image, total_bytes = qimg_to_bytesio(colony.icon_image)
                                info = tarfile.TarInfo(name=os.path.join(colony_path, 'icon_image.png'))
                                info.size = total_bytes
                                tf.addfile(tarinfo=info, fileobj=icon_image)
                            for event in colony:
                                event_name = str(round(event.happened)) + '-' + event.event
                                if event.image_before is not None:
                                    image_before, total_bytes = qimg_to_bytesio(event.image_before)
                                    info = tarfile.TarInfo(name=os.path.join(colony_path, event_name + '_before.png'))
                                    info.size = total_bytes
                                    tf.addfile(tarinfo=info, fileobj=image_before)
                                if event.image_after is not None:
                                    image_after, total_bytes = qimg_to_bytesio(event.image_after)
                                    info = tarfile.TarInfo(name=os.path.join(colony_path, event_name + '_after.png'))
                                    info.size = total_bytes
                                    tf.addfile(tarinfo=info, fileobj=image_after)

    def load_images(self, files=None):
        for animal in self:
            animal.load_images(base_path=self.base_path, files=files, recursive=True)

