
#include <math.h>
#include <complex>
#include <iostream> 
#include <vector>
#include <iomanip> // manipulating output 

using namespace std; 

std::vector<std::complex<double>> dft(std::vector<std::complex<double>> X)
{
    // determine number of samples 
    int N = X.size(); 
    int K = N; 

    // allocate memory for internals 
    std::complex<double> intSum; 

    // allocate memory for output 
    std::vector<std::complex<double>> output;
    output.reserve(K); 

    // loop through each K 
    for (int k=0; k<K; k++)
    {
        intSum = std::complex<double>(0,0);
        for(int n = 0; n<N; n++)
        {
            double realPart = cos(((2*M_PI)/N) * k * n);
            double imagPart = sin(((2*M_PI)/N) * k * n);
            // '-' term is from the original fourier equation 
            std::complex<double> w (realPart, -imagPart); 
            intSum += X[n] * w;
        }
        output.push_back(intSum);
    }
    return output;
}

int main()
{
    // create a test signal 
    int N = 1000;
    std::vector<std::complex<double>> signal; 
    signal.reserve(N); 

    double sigK = 3.0; 
    double sigPhase = 0.0;

    for(int x=0; x<N; ++x)
    {
        auto currentSample = std::complex<double> 
            (cos((2*M_PI/static_cast<double>(N)) *
                sigK * static_cast<double>(x) sigPhase), 0.0);
        signal.push_back(currentSample);
    }

    // compute the DFT
    std::vector<std::complex<double>> Fx = dft(signal);

    // display the first six values (real and imaginary components)
    std::cout << "****" << std::endl;
    std::cout << "First 6 samples of the output..." << std::endl;
    std::cout << "\n" << "k\t" << std:: setw(12)
        << "Real\t" << std::setw(12) << "Imag" << std::endl;
    for(int i=0; i<6; ++i)
    {
        std::cout << i << "\t"
            << std::setw(12) << Fx[i].real() / static_cast<double>(N) << "\t"
            << std::setw(12) << Fx[i].imag() / static_cast<double>(N)
            << std::endl; 
    }

    return 0;
}

 