@echo off
rem Copyright Intel Corporation.
rem 
rem This software and the related documents are Intel copyrighted materials,
rem and your use of them is governed by the express license under which they
rem were provided to you (License). Unless the License provides otherwise,
rem you may not use, modify, copy, publish, distribute, disclose or transmit
rem this software or the related documents without Intel's prior written
rem permission.
rem 
rem This software and the related documents are provided as is, with no
rem express or implied warranties, other than those that are expressly stated
rem in the License.

rem ----------------------------------------------------------------------------
rem mpiifort.bat
rem Simple script to compile and/or link MPI programs by Intel® Fortran Compiler.
rem ----------------------------------------------------------------------------

if "%1" == "" (
        call "%I_MPI_ROOT%\bin\mpifc.bat"
) else (
        call "%I_MPI_ROOT%\bin\mpifc.bat" -fc=ifort %*
)

