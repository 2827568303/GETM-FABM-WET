!! This file will be pre-processed by CMake generating *flexout_version.F90*
!! The module can be used by projects wanting to trace exact code information.

module flexout_version
   !! Version information will be optained from Git and includes *branch* and
   !! *hash* information.
   character(len=*),parameter :: git_commit_id = "0.1.0"
   character(len=*),parameter :: git_branch_name = "unknown"
end module
