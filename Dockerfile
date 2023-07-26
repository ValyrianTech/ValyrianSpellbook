# Use an official Python runtime as a parent image
FROM ubuntu:22.04

# Set the working directory in the container to /app
WORKDIR /

# Copy the current directory contents into the container at /app
ADD . /

# Update and upgrade the system
RUN apt-get update -y && apt-get upgrade -y

# Install any needed packages specified in requirements.txt
RUN apt-get install git python3.10 python3.10-dev python3-pip libssl-dev -y

# Clone the Valyrian Spellbook repository
RUN git clone https://github.com/ValyrianTech/ValyrianSpellbook.git spellbook

# Rename the example configuration file to spellbook.conf
RUN mv /spellbook/configuration/example_configuration_file.conf /spellbook/configuration/spellbook.conf

# Replace placeholders in the configuration file
# Add more RUN commands as needed to replace all placeholders
#RUN sed -i 's/^host=$/host=localhost/' /app/spellbook/configuration/spellbook.conf

# Install Python dependencies
RUN python3.10 -m pip install -r /spellbook/requirements.txt

# Make port 42069 available to the world outside this container
EXPOSE 42069

# Define environment variable
ENV NAME ValyrianSpellbook

# Run spellbookserver.py when the container launches
CMD ["python3.10", "/spellbook/spellbookserver.py"]