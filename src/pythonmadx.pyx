#-------------------------------------------------------------------------------
# This file is part of PyMad.
# 
# Copyright (c) 2013, M. Aiba. All rights reserved.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
# 	http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#-------------------------------------------------------------------------------

from string import *

cdef extern from "mad_def.h":
    cdef int NAME_L=48 # This is correct?? In mad_def.h, "#define NAME_L 48".

cdef extern from "mad_name.h":
    struct name_list:
       int curr
       int* inform
       char** names
       pass

cdef extern from "mad_array.h":
    struct char_p_array:
       int curr
       char** p
       pass


cdef extern from "mad_table.h":
    struct table:
       int curr
       int num_cols
       char* type
       char* name
       char_p_array* header
       char*** s_cols
       double** d_cols
       name_list* columns
       pass

cdef extern from "mad_core.h":
    void madx_start()
    void madx_finish()

cdef extern from "mad_eval.h":
    void pro_input_(char*)


cdef extern from "table_interface.h":
    table* my_get_twiss_table()

class dummyClass:
      def __init__(self,inDict):
            self.__dict__.update(inDict)

class madx:
      def __init__(self):
            madx_start()
            self.columns=[]

      def command(self,cmd):
            pro_input_(cmd)

      def finish(self):
            madx_finish()

      def twiss_table(self,columns=['NAME','S']):
            self.columns=columns
            if ('name' not in self.columns) and ('NAME' not in self.columns):
                  self.columns.append('NAME')

            cdef table* tptr
            tptr=my_get_twiss_table()

            # Structure members are accessible as python object!!
            # For example, tptr[0].columns.inform[0]

            inDict={}

            # Header
            inDict['NAME']=upper(tptr[0].name)
            inDict['TYPE']=upper(tptr[0].type)

            for i in range(0,tptr[0].header.curr):
                  s=tptr[0].header.p[i]
                  ss=s.split()
                  inDict[ss[1]]=ss[3]

            # Reconstruction of table contents

            label=tptr[0].columns.names
            dtype=tptr[0].columns.inform
            dat_index={}
            for i in range(0,tptr[0].num_cols):
                  if ((upper(label[i]) in self.columns) or 
                      (label[i] in self.columns)):
                        dat=[]
                        for j in range(0,tptr[0].curr):
                              if dtype[i]==3: # String data
                                    datj=tptr[0].s_cols[i][j]
                                    if str(label[i])=='name':
                                          sdatj=datj.split(":")
                                          datj=sdatj[0]
                                          dat_index[datj]=j
                                          dat_index[upper(datj)]=j
                                    dat.append(datj)
                              else: # Double or integer data
                                    dat.append(tptr[0].d_cols[i][j])
                        inDict[upper(label[i])]=dat
            inDict['indx']=dat_index

            # twiss table in memory with metaclass.twiss() style by Rogelio
            # Ex. (hor. beta at Q1) = tw.BETX[tw.indx['Q1']]
            tw=dummyClass(inDict) 
            tptr=NULL # This might not be mandatory.
            return tw



