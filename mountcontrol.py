#!/usr/bin/env python
'''Tree View/List Store

The GtkListStore is used to store data in list form, to be used
later on by a GtkTreeView to display it. This demo builds a
simple GtkListStore and displays it. See the Stock Browser
demo for a more advanced example.'''

import gobject
import gtk
import os
import csv

(
    COLUMN_FIXED,
    COLUMN_MOUNTPOINT,
    COLUMN_SEVERITY,
    COLUMN_DESCRIPTION
) = range(4)



dfout = os.popen('df').read().split("\n")

csv.register_dialect("fstab", delimiter=" ", lineterminator="\n")
reader = csv.reader(open("/etc/fstab.sshfs"),"fstab")


data = [];
for row in reader:
    # Existenz des Mountpoints in der Ausgabe von df suchen
    for line in dfout:
       col = line.split(" ")
       if col[len(col)-1] == row[0]:
          print line
          mounted = True
          break
       else:
          mounted = False

    data.append([mounted,row[0],row[1],row[2]])


# Datenarray in Tuple wandeln
data = tuple(data)


class mountcontrol(gtk.Window):
    def __init__(self, parent=None):
        # create window, etc
        gtk.Window.__init__(self)
        try:
            self.set_screen(parent.get_screen())
        except AttributeError:
            self.connect('destroy', lambda *w: gtk.main_quit())
        self.set_title(self.__class__.__name__)

        self.set_border_width(8)
        self.set_default_size(300, 250)

        vbox = gtk.VBox(False, 8)
        self.add(vbox)

        label = gtk.Label('sshfs Mounts')
        vbox.pack_start(label, False, False)

        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        vbox.pack_start(sw)

        # create tree model
        model = self.__create_model()

        # create tree view
        treeview = gtk.TreeView(model)
        treeview.set_rules_hint(True)
        treeview.set_search_column(COLUMN_DESCRIPTION)

        sw.add(treeview)

        # add columns to the tree view
        self.__add_columns(treeview)

        self.show_all()

    def __create_model(self):
        lstore = gtk.ListStore(
            gobject.TYPE_BOOLEAN,
            gobject.TYPE_STRING,
            gobject.TYPE_STRING,
            gobject.TYPE_STRING)

        for item in data:
            iter = lstore.append()
            lstore.set(iter,
                COLUMN_FIXED, item[COLUMN_FIXED],
                COLUMN_MOUNTPOINT, item[COLUMN_MOUNTPOINT],
                COLUMN_SEVERITY, item[COLUMN_SEVERITY],
                COLUMN_DESCRIPTION, item[COLUMN_DESCRIPTION])
        return lstore

    def fixed_toggled(self, cell, path, model):
        # get toggled iter
        iter = model.get_iter((int(path),))
        fixed = model.get_value(iter, COLUMN_FIXED)

        # do something with the value
        fixed = not fixed
        mp = model.get_value(iter, COLUMN_MOUNTPOINT)
        if fixed: 
             print "mount item %s " % mp
             cmd = "mount " + mp
        else:
             print "umount item %s " % mp
             cmd = "fusermount -u " + mp       
        os.system(cmd)
        # set new value
        model.set(iter, COLUMN_FIXED, fixed)

    def __add_columns(self, treeview):
        model = treeview.get_model()

        # column for fixed toggles
        renderer = gtk.CellRendererToggle()
        renderer.connect('toggled', self.fixed_toggled, model)

        column = gtk.TreeViewColumn('on/off', renderer, active=COLUMN_FIXED)

        # set this column to a fixed sizing(of 50 pixels)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        column.set_fixed_width(50)

        treeview.append_column(column)

        # column for bug numbers
        column = gtk.TreeViewColumn('Mountpoint', gtk.CellRendererText(),
                                    text=COLUMN_MOUNTPOINT)
        column.set_sort_column_id(COLUMN_MOUNTPOINT)
        treeview.append_column(column)

        # columns for severities
        column = gtk.TreeViewColumn('Host', gtk.CellRendererText(),
                                    text=COLUMN_SEVERITY)
        column.set_sort_column_id(COLUMN_SEVERITY)
        treeview.append_column(column)

        # column for description
        column = gtk.TreeViewColumn('Path', gtk.CellRendererText(),
                                     text=COLUMN_DESCRIPTION)
        column.set_sort_column_id(COLUMN_DESCRIPTION)
        treeview.append_column(column)

def main():
    mountcontrol()
    gtk.main()

if __name__ == '__main__':
    main()
