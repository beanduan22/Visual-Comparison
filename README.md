
# Run the tool
OpenCV-Testing is a tool of fuzzing Opencv-python, you can run main.py directly.

# standarized API info
you can find in 
```
OpenCV-Testing/API_info.py
```

# Docker and OpenCV Coverage Setup

Follow these steps to build and run a Docker container for OpenCV code coverage testing, and generate a coverage report.

1. **Build Dockerfile**
    ```bash
    docker build -t opencv-coverage .
    ```

2. **Run Docker Container**
    ```bash
    docker run -it --rm -v "Your_Location\cover_opencv\new_cov\opencv_docker_code_coverages\OpenCV-Testing:/app" --name opencv_coverage_container_1 opencv-coverage
    ```

3. **Check the Files**
    ```bash
    ls -l
    ```

4. **Run Python Script**
    ```bash
    python3 main.py
    ```

5. **Navigate to OpenCV Build Directory**
    ```bash
    cd /usr/local/src/opencv/build/
    ```

6. **Install gcovr**
    ```bash
    pip install gcovr
    ```

7. **Generate Coverage Report**
    ```bash
    gcovr -r /usr/local/src/opencv --html --html-details -o coverage_report.html
    ```

8. **Find Container ID**
    ```bash
    docker ps
    ```

9. **Copy Coverage Report to Host**
    ```bash
    docker cp <container_id>:/usr/local/src/opencv/build/coverage_report.html <path_on_host>
    ```
    Example:
    ```bash
    docker cp c4f9932f08ee:/usr/local/src/opencv/build/coverage_report.html .
    ```

10. **Open Coverage Report**
    - **macOS:**
      ```bash
      open <path_on_host>/coverage_report.html
      ```
    - **Windows:**
      ```bash
      start <path_on_host>\coverage_report.html
      ```
    - **Linux:**
      ```bash
      xdg-open <path_on_host>/coverage_report.html
      ```
```
