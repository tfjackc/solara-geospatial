# Use the official Jupyter base-notebook image based on Python 3.9 from Docker Hub
FROM jupyter/base-notebook:python-3.9.6

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install Python packages from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Create a directory for your application pages
RUN mkdir ./pages

# Copy the pages folder into the container
COPY pages ./pages

# Copy the portalWebMaps_Test.csv data file into the container
COPY data/portalWebMaps_Test.csv ./data/portalWebMaps_Test.csv

# Set the environment variable for PROJ_LIB
ENV PROJ_LIB='/opt/conda/share/proj'

# Change ownership of the home directory to the NB_UID (non-root user)
USER root
RUN chown -R ${NB_UID} ${HOME}
USER ${NB_USER}

# Expose port 8765 (if your application uses this port)
EXPOSE 8765

# Set the default command to run your application using solara
CMD ["solara", "run", "./pages", "--host=0.0.0.0"]
