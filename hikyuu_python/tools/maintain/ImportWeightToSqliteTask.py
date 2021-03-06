# coding:utf-8
#
# The MIT License (MIT)
#
# Copyright (c) 2010-2017 fasiondog/hikyuu
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import sqlite3
import urllib.request

from tdx_to_h5 import qianlong_import_weight

class ImportWeightToSqliteTask:
    def __init__(self, queue, sqlitefile, dest_dir):
        self.queue = queue
        self.sqlitefile = sqlitefile
        self.dest_dir = dest_dir
        self.msg_name = 'IMPORT_WEIGHT'

    def __call__(self):
        total_count = 0
        try:
            self.queue.put([self.msg_name, '正在下载...', 0, 0, 0])
            connect = sqlite3.connect(self.sqlitefile)
            net_file = urllib.request.urlopen('http://www.qianlong.com.cn/download/history/weight.rar', timeout=60)
            dest_filename = self.dest_dir+'/weight.rar'
            with open(dest_filename, 'wb') as file:
                file.write(net_file.read())

            self.queue.put([self.msg_name, '下载完成，正在解压...', 0, 0, 0])
            os.system('unrar x -o+ -inul {} {}'.format(dest_filename, self.dest_dir))

            self.queue.put([self.msg_name, '解压完毕，正在导入权息数据...', 0, 0, 0])
            total_count = qianlong_import_weight(connect, self.dest_dir + '/weight', 'SH')
            total_count += qianlong_import_weight(connect, self.dest_dir + '/weight', 'SZ')
            self.queue.put([self.msg_name, '导入完成!', 0, 0, total_count])

        except Exception as e:
            self.queue.put([self.msg_name, str(e), -1, 0, total_count])

        self.queue.put([self.msg_name, '', 0, None, total_count])
