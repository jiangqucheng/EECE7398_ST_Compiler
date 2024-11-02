// projectile_motion.cpp
#include <iostream>
#include <cmath>

void simulate_projectile(double angle, double velocity, int steps) {
    const double g = 9.81; // Gravity
    double t = 0.0;        // Time
    double dt = 0.01;      // Time step
    double x = 0.0;        // X position
    double y = 0.0;        // Y position

    double vx = velocity * cos(angle * M_PI / 180.0); // X component of velocity
    double vy = velocity * sin(angle * M_PI / 180.0); // Y component of velocity

    for (int i = 0; i < steps; i++) {
        t += dt;
        x += vx * dt;
        y += vy * dt;
        
        // Apply air resistance and gravity (including float divisions)
        vx *= 1.0 - dt / 5.0;
        vy -= g * dt / 2.0;

        if (y < 0) break; // Stop when projectile hits the ground
    }

    std::cout << "Final position: (" << x << ", " << y << ")" << std::endl;
}

int main() {
    simulate_projectile(45.0, 30.0, 1000);
    return 0;
}
