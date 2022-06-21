Check OpenCL driver: (https://support.zivid.com/v2.4/getting-started/software-installation/gpu/install-opencl-drivers-ubuntu.html)
    sudo apt install -y clinfo
must check cl:
    sudo /usr/bin/clinfo
    /usr/bin/clinfo -l

when i got error:
    CL/cl.hpp: No such file or directory
installed:
    apt-get install opencl-headers
run:
    g++ OpenCL_primjeri/kostur.cpp -o kostur -I./OpenCL/include -L./OpenCL/lib -lOpenCL

