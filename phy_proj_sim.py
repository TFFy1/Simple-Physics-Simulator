import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.animation as animation
from matplotlib.widgets import Button

# Constants
car_mass = 2000  # Mass of the car in kg
platform_mass = 500  # Mass of the platform in kg
counterweight_mass = 1500  # Counterweight mass in kg
elevator_height = 50  # Height of the elevator in meters
g = 9.81  # Gravity in m/s^2
elevator_time = 60  # Total time to lift in seconds (1 minute for full trip)
motor_efficiency = 0.8  # Motor efficiency (fraction)
reservoir_capacity = 25000  # Total water capacity in kg
friction_coefficient = 0.35  # Coefficient of friction between cable and pulley

# Effective mass for upward and downward trips
m_eff_up = platform_mass + car_mass - counterweight_mass
m_eff_down = platform_mass - counterweight_mass

# Forces for upward and downward trips
F_gravity_up = m_eff_up * g
F_friction_up = friction_coefficient * F_gravity_up
F_gravity_down = abs(m_eff_down) * g
F_friction_down = friction_coefficient * F_gravity_down

# Energy needed for upward and downward trips
work_up = (F_gravity_up + F_friction_up) * elevator_height
energy_needed_up = work_up / motor_efficiency
work_down = (F_gravity_down + F_friction_down) * elevator_height
energy_needed_down = work_down / motor_efficiency

# Initial conditions
water_top = reservoir_capacity
water_bottom = 0
energy_generated = 0
elevator_position = 0
counterweight_position = elevator_height
is_moving_up = True

# Set up the plot
fig, ax = plt.subplots(figsize=(10, 8))
ax.set_xlim(0, 15)
ax.set_ylim(0, elevator_height + 10)

is_running = False  # Global state to track if the animation is running


def toggle_animation(event):
    """Toggle the animation state between play and pause."""
    global is_running
    if is_running:
        ani.event_source.stop()
        play_button.label.set_text("Play")
    else:
        ani.event_source.start()
        play_button.label.set_text("Pause")
    is_running = not is_running


# Add button for play/pause control
button_ax = plt.axes([0.8, 0.02, 0.1, 0.05])  # x, y, width, height of the button
play_button = Button(button_ax, "Play")
play_button.on_clicked(toggle_animation)

# Reservoir visuals
top_reservoir = patches.Rectangle((10, elevator_height + 5), 3, -5, color="blue")
bottom_reservoir = patches.Rectangle((10, 0), 3, 5, color="blue")
ax.add_patch(top_reservoir)
ax.add_patch(bottom_reservoir)

# Elevator visuals
platform = patches.Rectangle((5, 0), 3, 1, color="gray", label="Platform (500 kg)")
car = patches.Rectangle((5.5, 1), 2, 1, color="black", label="Car (2000 kg)")
ax.add_patch(platform)
ax.add_patch(car)

# Counterweight visuals
counterweight = patches.Rectangle((2, elevator_height), 2, 2, color="green", label="Counterweight(1500 kg)")
ax.add_patch(counterweight)

# Cable visuals
cable_elevator, = ax.plot([6.5, 6.5], [1, elevator_height], color="black", linestyle="--")
cable_counterweight, = ax.plot([3, 3], [elevator_height, 0], color="black", linestyle="--")

# Text for water volumes and flow rate
water_text_top = ax.text(11.5, elevator_height + 7, f"Water: {reservoir_capacity:.1f} kg", fontsize=10, ha="center")
water_text_bottom = ax.text(11.5, 7, f"Water: {water_bottom:.1f} kg", fontsize=10, ha="center")
flow_rate_text = ax.text(11.5, 3, f"Flow Rate: 0.00 kg/s", fontsize=10, ha="center", color="blue")


# Animation update function
platform_mass_text = ax.text(5, elevator_height + 2, f"Mass: {platform_mass + car_mass:.1f} kg", 
                             fontsize=10, color="red", ha="center")

def update(frame):
    global water_top, water_bottom, energy_generated, elevator_position, counterweight_position, is_moving_up

    # Stop if out of water
    if water_top <= 0:
        ani.event_source.stop()
        play_button.label.set_text("Restart")
        return

    # Determine current force, energy requirements, and flow rate
    if is_moving_up:
        force = F_gravity_up + F_friction_up
        energy_required = force * (elevator_height / elevator_time)
        current_flow_rate = energy_required / (g * elevator_height * motor_efficiency)

        # Ensure water is available for this frame
        if water_top >= current_flow_rate:
            water_top -= current_flow_rate
            water_bottom += current_flow_rate
            energy_generated += current_flow_rate * g * elevator_height * motor_efficiency
        else:
            current_flow_rate = water_top
            water_bottom += water_top
            water_top = 0
            energy_generated += current_flow_rate * g * elevator_height * motor_efficiency

        # Move elevator if energy is sufficient
        if energy_generated >= energy_required:
            elevator_position += elevator_height / elevator_time
            counterweight_position -= elevator_height / elevator_time
            car.set_y(elevator_position + 1)
            energy_generated -= energy_required

        # Switch to downward trip at the top
        if elevator_position >= elevator_height:
            is_moving_up = False
            car.set_visible(False)

    else:
        force = F_gravity_down + F_friction_down
        energy_required = force * (elevator_height / elevator_time)
        current_flow_rate = energy_required / (g * elevator_height * motor_efficiency)

        if water_top >= current_flow_rate:
            water_top -= current_flow_rate
            water_bottom += current_flow_rate
            energy_generated += current_flow_rate * g * elevator_height * motor_efficiency
        else:
            current_flow_rate = water_top
            water_bottom += water_top
            water_top = 0
            energy_generated += current_flow_rate * g * elevator_height * motor_efficiency

        if energy_generated >= energy_required:
            elevator_position -= elevator_height / elevator_time
            counterweight_position += elevator_height / elevator_time
            energy_generated -= energy_required

        if elevator_position <= 0:
            ani.event_source.stop()
            play_button.label.set_text("Restart")
            return

    # Update visuals
    platform.set_y(elevator_position)
    counterweight.set_y(counterweight_position)

    cable_elevator.set_data([6.5, 6.5], [elevator_position + 1, elevator_height])
    cable_counterweight.set_data([3, 3], [counterweight_position + 2, elevator_height])

    top_reservoir.set_height(-5 * (water_top / reservoir_capacity))
    bottom_reservoir.set_height(5 * (water_bottom / reservoir_capacity))

    # Update text
    water_text_top.set_text(f"Water: {max(water_top, 0):.1f} kg")
    water_text_bottom.set_text(f"Water: {min(water_bottom, reservoir_capacity):.1f} kg")
    flow_rate_text.set_text(f"Flow Rate: {current_flow_rate:.2f} kg/s")

    # Update mass text on the platform
    if is_moving_up:
        current_mass = platform_mass + car_mass
    else:
        current_mass = platform_mass
    platform_mass_text.set_text(f"Mass: {current_mass:.1f} kg")
    platform_mass_text.set_y(elevator_position + 3)

    return (top_reservoir, bottom_reservoir, platform, car, counterweight,
            water_text_top, water_text_bottom, flow_rate_text, platform_mass_text)


# Create animation
ani = animation.FuncAnimation(fig, update, frames=range(elevator_time * 2 + 1), interval=100, blit=False)

# Plot labels and legend
ax.set_title("Elevator and Water Flow Simulation")
ax.set_xlabel("Horizontal Position")
ax.set_ylabel("Vertical Position (m)")
ax.legend(loc='upper right')

plt.show()
