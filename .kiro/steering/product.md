# Product Overview

AI-powered medical clinic appointment system that handles patient registration and appointment scheduling through conversational interface.

## Core Functionality

- Patient registration and data management (CPF-based identification)
- Medical appointment scheduling with specialty selection
- Appointment cancellation and confirmation
- Appointment queries with flexible filtering
- Conversational AI interface using LangGraph agents

## Key Entities

- Paciente (Patient/Client)
- Médico (Doctor) with specialties and availability
- Consulta (Appointment)
- Procedimento (Medical Procedure)

## User Flow

1. Patient initiates chat and provides CPF
2. System checks if patient exists; if not, proceeds to registration
3. Patient selects action from menu: schedule, cancel, confirm, or query appointments
4. After each action, patient can exit or return to menu
