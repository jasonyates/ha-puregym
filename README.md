# PureGym for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

A Home Assistant integration to monitor attendance at your home PureGym. Exposes a single sensor named `puregym_attendance` and updates every 15 minutes.

This integration is in no way affiliated to PureGym.

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the three dots menu → Custom repositories
3. Add this repository URL with category "Integration"
4. Search for "PureGym" and install
5. Restart Home Assistant

### Manual

1. Copy the `custom_components/puregym` folder to your `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

1. Go to Settings → Devices & Services
2. Click "Add Integration"
3. Search for "PureGym"
4. Enter your PureGym email and PIN
5. Optionally adjust the update interval (default: 15 minutes)

## Sensor

The integration creates a sensor showing the current attendance at your home gym:

- **Entity**: `sensor.puregym_attendance`
- **State**: Number of people currently at the gym
- **Attributes**: `gym_name`, `last_updated`
