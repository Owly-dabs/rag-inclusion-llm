# Repository: `fastai/fastai` — Issue #40

## Code region 1

```
from .imports import *
from .torch_imports import *
from sklearn.metrics import confusion_matrix


def plots(ims, figsize=(12,6), rows=1, interp=False, titles=None, maintitle=None):
    if type(ims[0]) is np.ndarray:
        ims = np.array(ims)
        if (ims.shape[-1] != 3): ims = ims.transpose((0,2,3,1))
    f = plt.figure(figsize=figsize)
```

### Explanation:

To address the issue described and implement the necessary changes to the image plotting functionality, we need to modify the `plots` function in the provided code. The goal is to remove the restriction that causes a `ValueError` when the number of images doesn't fit into a predefined grid, thereby allowing more flexible plotting of images.

### Code Changes:

1. **Remove Restriction on Number of Rows:**
   - The current implementation might have a restriction that checks if the number of rows is zero or if the images fit into a specific grid. We need to remove or adjust this restriction to allow any number of rows.

2. **Dynamic Grid Calculation:**
   - Implement logic to dynamically calculate the number of columns based on the number of images and the specified number of rows. This will ensure that images can be plotted even if they don't fit into a predefined grid.

3. **Error Handling:**
   - Add error handling to manage scenarios where the number of images is less than the number of rows or other edge cases that might arise from the new flexibility.

### Example Code Modification:

```python
def plots(ims, figsize=(12,6), rows=1, interp=False, titles=None, maintitle=None):
    if type(ims[0]) is np.ndarray:
        ims = np.array(ims)
        if (ims.shape[-1] != 3): ims = ims.transpose((0,2,3,1))
    
    # Calculate the number of columns dynamically
    cols = len(ims) // rows + (len(ims) % rows > 0)
    
    # Create the figure and axes
    f, axes = plt.subplots(rows, cols, figsize=figsize)
    axes = axes.flatten() if rows > 1 else [axes]
    
    # Plot each image
    for i, ax in enumerate(axes):
        if i < len(ims):
            ax.imshow(ims[i], interpolation=None if interp else 'none')
            ax.axis('off')
            if titles is not None:
                ax.set_title(titles[i], fontsize=12)
        else:
            ax.axis('off')  # Hide any unused subplots

    if maintitle:
        plt.suptitle(maintitle, fontsize=16)
    plt.tight_layout()
    plt.show()
```

### Explanation:

- **Dynamic Columns Calculation:** The number of columns is calculated based on the total number of images and the specified number of rows. This ensures that all images are plotted without requiring a fixed grid size.
  
- **Flattening Axes:** The axes are flattened to simplify the plotting process, especially when dealing with multiple rows.

- **Error Handling:** The code includes logic to hide unused subplots, preventing errors when the number of images is less than the total number of subplots.

These changes enhance the flexibility and usability of the plotting function, allowing users to plot images in a variety of configurations without encountering errors related to grid constraints.

## Code region 2

```
ims = np.array(ims)
        if (ims.shape[-1] != 3): ims = ims.transpose((0,2,3,1))
    f = plt.figure(figsize=figsize)
    if maintitle is not None:
        plt.suptitle(maintitle, fontsize=16)
    for i in range(len(ims)):
        sp = f.add_subplot(rows, len(ims)//rows, i+1)
        sp.axis('Off')
        if titles is not None: sp.set_title(titles[i], fontsize=16)
        plt.imshow(ims[i], interpolation=None if interp else 'none')


def plots_from_files(imspaths, figsize=(10,5), rows=1, titles=None, maintitle=None):
```

### Explanation:

To address the issue described and implement the necessary changes for flexible image plotting, the following code modifications are required:

### Current Code Context:
```python
ims = np.array(ims)
if (ims.shape[-1] != 3): ims = ims.transpose((0,2,3,1))
f = plt.figure(figsize=figsize)
if maintitle is not None:
    plt.suptitle(maintitle, fontsize=16)
for i in range(len(ims)):
    sp = f.add_subplot(rows, len(ims)//rows, i+1)
    sp.axis('Off')
    if titles is not None: sp.set_title(titles[i], fontsize=16)
    plt.imshow(ims[i], interpolation=None if interp else 'none')

def plots_from_files(imspaths, figsize=(10,5), rows=1, titles=None, maintitle=None):
```

### Proposed Changes:

1. **Dynamic Calculation of Columns:**
   - Instead of fixing the number of columns based on integer division (`len(ims)//rows`), calculate the number of columns dynamically to accommodate any number of images.

2. **Error Handling for Zero Rows:**
   - Add a check to ensure that the number of rows is not zero to prevent division by zero errors.

3. **Flexible Grid Layout:**
   - Allow the grid layout to adjust based on the total number of images and specified rows, ensuring that all images are plotted without errors.

### Modified Code:
```python
def plots_from_files(imspaths, figsize=(10,5), rows=1, titles=None, maintitle=None):
    ims = [plt.imread(path) for path in imspaths]
    ims = np.array(ims)
    if ims.shape[-1] != 3:
        ims = ims.transpose((0, 2, 3, 1))
    
    # Ensure rows is not zero to avoid division by zero
    if rows <= 0:
        raise ValueError("Number of rows must be greater than zero.")
    
    # Calculate the number of columns dynamically
    cols = (len(ims) + rows - 1) // rows  # Ceiling division to ensure all images are plotted
    
    f = plt.figure(figsize=figsize)
    if maintitle is not None:
        plt.suptitle(maintitle, fontsize=16)
    
    for i in range(len(ims)):
        sp = f.add_subplot(rows, cols, i + 1)
        sp.axis('Off')
        if titles is not None:
            sp.set_title(titles[i], fontsize=16)
        plt.imshow(ims[i], interpolation=None if interp else 'none')

# Example usage
# plots_from_files(['path/to/image1.png', 'path/to/image2.png'], rows=2)
```

### Explanation of Changes:
- **Dynamic Columns Calculation:** The number of columns is calculated using ceiling division to ensure that all images are accommodated in the grid, even if the number of images doesn't perfectly divide by the number of rows.
- **Error Handling:** A check is added to ensure that the number of rows is greater than zero, preventing potential errors from invalid input.
- **Flexible Layout:** These changes allow for a more flexible and user-friendly plotting experience, accommodating various numbers of images without predefined grid constraints.

## Code region 3

```
titles (list): list of titles
        maintitle (string): main title
    """
    f = plt.figure(figsize=figsize)
    if maintitle is not None: plt.suptitle(maintitle, fontsize=16)
    for i in range(len(imspaths)):
        sp = f.add_subplot(rows, len(imspaths)//rows, i+1)
        sp.axis('Off')
        if titles is not None: sp.set_title(titles[i], fontsize=16)
        img = plt.imread(imspaths[i])
        plt.imshow(img)
```

### Explanation:

To address the issue described and implement the necessary changes for flexible image plotting, we need to modify the code responsible for plotting images. The current code snippet provided in the `code_context` section shows how images are plotted using a fixed number of rows, which can lead to errors if the number of images doesn't fit into the specified grid. Here's how you can modify the code to allow for more flexible plotting:

### Current Code:
```python
f = plt.figure(figsize=figsize)
if maintitle is not None: plt.suptitle(maintitle, fontsize=16)
for i in range(len(imspaths)):
    sp = f.add_subplot(rows, len(imspaths)//rows, i+1)
    sp.axis('Off')
    if titles is not None: sp.set_title(titles[i], fontsize=16)
    img = plt.imread(imspaths[i])
    plt.imshow(img)
```

### Proposed Changes:
1. **Dynamic Calculation of Columns**: Instead of relying on a fixed number of rows, calculate the number of columns dynamically based on the total number of images and the specified number of rows.

2. **Handle Edge Cases**: Ensure that the code can handle cases where the number of images doesn't perfectly divide into the specified number of rows, by adjusting the number of columns accordingly.

3. **Error Handling**: Add error handling to manage scenarios where the number of images is less than the number of rows or other potential edge cases.

### Modified Code:
```python
import math

f = plt.figure(figsize=figsize)
if maintitle is not None:
    plt.suptitle(maintitle, fontsize=16)

# Calculate the number of columns dynamically
num_images = len(imspaths)
cols = math.ceil(num_images / rows) if rows > 0 else num_images

for i in range(num_images):
    sp = f.add_subplot(rows, cols, i + 1)
    sp.axis('Off')
    if titles is not None:
        sp.set_title(titles[i], fontsize=16)
    img = plt.imread(imspaths[i])
    plt.imshow(img)

# Optional: Add error handling for edge cases
if rows <= 0:
    raise ValueError("Number of rows must be greater than zero.")
if num_images < rows:
    raise ValueError("Number of images is less than the number of rows.")
```

### Explanation of Changes:
- **Dynamic Columns**: The number of columns is calculated using `math.ceil(num_images / rows)`, which ensures that all images are accommodated even if the number of images doesn't perfectly divide by the number of rows.
- **Error Handling**: Added checks to ensure that the number of rows is greater than zero and that the number of images is not less than the number of rows, which prevents potential errors.
- **Flexibility**: This change allows users to specify any number of rows, and the code will adjust the number of columns accordingly, providing a more flexible and error-free plotting experience.

These changes enhance the functionality and usability of the image plotting feature, allowing users to plot images in a grid layout that best fits their needs without encountering errors due to rigid constraints.

## Code region 4

```
plt.ylabel('True label')
    plt.xlabel('Predicted label')

def plots_raw(ims, figsize=(12,6), rows=1, titles=None):
    f = plt.figure(figsize=figsize)
    for i in range(len(ims)):
        sp = f.add_subplot(rows, len(ims)//rows, i+1)
        sp.axis('Off')
        if titles is not None: sp.set_title(titles[i], fontsize=16)
        plt.imshow(ims[i])

def load_img_id(ds, idx, path): return np.array(PIL.Image.open(path+ds.fnames[idx]))
```

### Explanation:

To address the issue described in the summary and enhance the flexibility of the image plotting functionality, we need to make changes to the `plots_raw` function in the provided code context. The goal is to allow the plotting of images even when the number of images does not fit into a predefined grid, thereby avoiding errors like `ValueError`.

### Code Changes:

1. **Adjust the Grid Calculation**:
   - Modify the calculation of the number of columns to accommodate scenarios where the number of images does not divide evenly by the number of rows. This can be done using the `ceil` function from the `math` module to ensure that all images are plotted.

2. **Import Required Modules**:
   - Ensure that the `math` module is imported to use the `ceil` function.

3. **Handle Edge Cases**:
   - Add checks to handle cases where the number of images is less than the number of rows or when the number of rows is zero.

### Updated Code:

```python
import matplotlib.pyplot as plt
import numpy as np
import PIL
import math

def plots_raw(ims, figsize=(12,6), rows=1, titles=None):
    if rows <= 0:
        raise ValueError("Number of rows must be greater than zero.")
    if len(ims) < rows:
        raise ValueError("Number of images must be greater than or equal to the number of rows.")
    
    cols = math.ceil(len(ims) / rows)
    f = plt.figure(figsize=figsize)
    for i in range(len(ims)):
        sp = f.add_subplot(rows, cols, i+1)
        sp.axis('Off')
        if titles is not None: 
            sp.set_title(titles[i], fontsize=16)
        plt.imshow(ims[i])

def load_img_id(ds, idx, path): 
    return np.array(PIL.Image.open(path + ds.fnames[idx]))
```

### Explanation of Changes:

1. **Import `math` Module**:
   - The `math` module is imported to use the `ceil` function, which is necessary for calculating the number of columns when the number of images does not divide evenly by the number of rows.

2. **Grid Calculation**:
   - The number of columns is calculated using `math.ceil(len(ims) / rows)`. This ensures that all images are plotted, even if the number of images is not perfectly divisible by the number of rows.

3. **Error Handling**:
   - Added checks to ensure that the number of rows is greater than zero and that the number of images is greater than or equal to the number of rows. This prevents potential errors and ensures valid input.

These changes will make the image plotting functionality more flexible and user-friendly, allowing for a wider range of image display configurations without encountering errors.

---

# Repository: `PrefectHQ/prefect` — Issue #3549

## Code region 1

```
def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.validators.insert(0, self._validate_json)

    def _serialize(self, value, attr, obj, **kwargs):  # type: ignore
        self._validate_json(value)
        return super()._serialize(value, attr, obj, **kwargs)

    def _validate_json(self, value: Any) -> None:
        try:
            json.dumps(value)
        except TypeError as type_error:
            raise ValidationError("Value is not JSON-compatible") from type_error


class Nested(fields.Nested):
    """
    An extension of the Marshmallow Nested field that allows the value to be selected
    via a value_selection_fn.
```

### Explanation:

To address the issue of unclear error messages when registering a flow with default parameters that are not JSON serializable in Prefect Cloud, the following code changes need to be made:

1. **Update the Error Message in `_validate_json` Method:**

   The current implementation of the `_validate_json` method raises a generic `ValidationError` with the message "Value is not JSON-compatible". To provide more informative error messages, this message should be updated to include specific details about the parameter that caused the error and why it is not JSON serializable.

   **Code Change:**

   ```python
   def _validate_json(self, value: Any) -> None:
       try:
           json.dumps(value)
       except TypeError as type_error:
           raise ValidationError(f"Parameter default value '{value}' is not JSON-compatible. Ensure all default values are JSON serializable.") from type_error
   ```

   **Reason for Change:**

   By including the actual value that caused the error in the message, developers can quickly identify which parameter default is problematic. Additionally, providing guidance on ensuring JSON serialization compatibility helps developers understand how to resolve the issue.

2. **Enhance the Context of the Error Message:**

   Consider adding more context to the error message to help developers understand the broader context of the error, such as which flow or parameter is affected.

   **Code Change:**

   ```python
   def _validate_json(self, value: Any, param_name: str = "") -> None:
       try:
           json.dumps(value)
       except TypeError as type_error:
           raise ValidationError(
               f"Parameter '{param_name}' default value '{value}' is not JSON-compatible. "
               "Ensure all default values are JSON serializable."
           ) from type_error
   ```

   **Reason for Change:**

   Including the parameter name in the error message provides additional context, making it easier for developers to pinpoint the exact source of the issue within their flow.

3. **Modify the Call to `_validate_json` to Pass Parameter Name:**

   Ensure that when `_validate_json` is called, the parameter name is passed so that it can be included in the error message.

   **Code Change:**

   ```python
   def _serialize(self, value, attr, obj, **kwargs):  # type: ignore
       self._validate_json(value, attr)
       return super()._serialize(value, attr, obj, **kwargs)
   ```

   **Reason for Change:**

   Passing the parameter name to `_validate_json` allows the enhanced error message to include specific information about which parameter's default value is causing the JSON serialization issue.

By implementing these changes, the error messages will become more informative and actionable, significantly improving the developer experience when working with Prefect Cloud. This will help developers quickly identify and resolve issues related to JSON serialization of parameter defaults.

---

# Repository: `h2oai/h2o-3` — Issue #3

## Code region 1

```
// Now look for a pre-cooked Icer.  No locking, 'cause we're just looking
    String icer_name = implClazzName(iced_name);
    CtClass icer_cc = _pool.getOrNull(icer_name); // Full Name Lookup of Icer
    if( icer_cc != null ) {
      synchronized( iced_clazz ) {
        if( !icer_cc.isFrozen() ) icer_cc.toClass(); // Load class (but does not link & init)
        return Class.forName(icer_name); // Found a pre-cooked Icer implementation
      }
    }

    // Serialize parent.  No locking; occasionally we'll "onIce" from the
    // remote leader more than once.
```

### Explanation:

To address the class loading issue described, the code changes need to focus on modifying how Javassist interacts with the classloader in the context of the Weaver tool. The problem arises because Javassist's default behavior is to use the thread's context classloader, which is altered by scalatest to be a child URLClassLoader. This setup causes class loading failures when attempting to dynamically load classes that have been manipulated by Javassist.

### Code Changes Required

1. **Explicitly Set the ClassLoader for Javassist:**
   Modify the code to ensure that Javassist uses a specific classloader instead of the thread's context classloader. This involves changing the way `CtClass.toClass()` is invoked to include the appropriate classloader.

2. **Modify the `CtClass.toClass()` Invocation:**
   In the code snippet provided, the line `icer_cc.toClass();` should be modified to explicitly pass the current classloader. This can be done by using `icer_cc.toClass(currentClassLoader, null);` where `currentClassLoader` is a reference to the classloader that has the necessary visibility of the classes.

3. **Determine the Appropriate ClassLoader:**
   Identify the classloader that should be used. This is typically the classloader of the current class or the parent classloader in the hierarchy that has access to all necessary classes. You can obtain it using `this.getClass().getClassLoader()` or `ClassLoader.getSystemClassLoader()` depending on the specific requirements and setup.

### Why These Changes Are Necessary

- **Resolve Class Loading Conflicts:**
  By explicitly setting the classloader, you ensure that Javassist loads classes from the correct classloader, avoiding the issue where `Class.forName()` fails to find classes because it searches in the parent classloader instead of the child.

- **Maintain Compatibility with Testing Frameworks:**
  These changes ensure compatibility with scalatest and other testing frameworks that might alter the thread context classloader, preventing class loading issues during testing.

- **Improve Stability and Reliability:**
  The changes lead to more stable and reliable test executions by ensuring that dynamically loaded classes are correctly found and loaded, particularly in environments with complex classloader hierarchies.

- **Adopt Best Practices:**
  Explicitly managing classloaders in environments with multiple classloaders is a best practice that helps avoid subtle bugs and ensures robust and maintainable code.

By implementing these changes, you address the root cause of the class loading issue and ensure that the Weaver tool and Javassist function correctly within the testing environment set by scalatest.

## Code region 2

```
// class, but also to allow parallel class-gens of unrelated Iced).
    //noinspection SynchronizationOnLocalVariableOrMethodParameter
    synchronized( iced_clazz ) {
      icer_cc = _pool.getOrNull(icer_name); // Retry under lock
      if( icer_cc != null ) return Class.forName(icer_name); // Found a pre-cooked Icer implementation
      icer_cc = genIcerClass(id,iced_cc,iced_clazz,icer_name,super_id,super_icer_cc,super_has_jfields);
      icer_cc.toClass();               // Load class (but does not link & init)
      return Class.forName(icer_name); // Initialize class now, before subclasses
    }
  }

  // Generate the Icer class
  private static CtClass genIcerClass(int id, CtClass iced_cc, Class iced_clazz, String icer_name, int super_id, CtClass super_icer, boolean super_has_jfields ) throws CannotCompileException, NotFoundException, NoSuchFieldException {
```

### Explanation:

To address the class loading issue described, modifications need to be made to the code to ensure that Javassist uses the correct classloader when loading classes. The problem arises because the default behavior of Javassist is to use the thread context classloader, which is altered by scalatest to be a child URLClassLoader. This setup causes class loading failures, particularly when trying to load classes that have been manipulated by Javassist.

### Code Changes

1. **Modify Class Loading Strategy**: 
   - Instead of relying on the thread context classloader, explicitly set the classloader used by Javassist to the current classloader. This ensures that the classes are loaded in the correct classloader hierarchy, avoiding the child classloader introduced by scalatest.

2. **Update `CtClass.toClass()` Invocation**:
   - When invoking `CtClass.toClass()`, pass the appropriate classloader. This can be done by obtaining the current classloader using `getClass().getClassLoader()` or a similar method, depending on the context in which the code is running.

3. **Ensure Consistency Across Class Loading**:
   - Make sure that all instances where classes are loaded or manipulated by Javassist are consistent with the new class loading strategy. This might involve updating other parts of the code where `Class.forName()` or similar methods are used.

### Example Code Adjustment

Here's a conceptual example of how you might adjust the code:

```java
// Before: Using default thread context classloader
icer_cc.toClass(); // This uses the thread context classloader by default

// After: Explicitly setting the classloader
ClassLoader currentClassLoader = getClass().getClassLoader();
icer_cc.toClass(currentClassLoader, null); // Pass the current classloader explicitly
```

### Why These Changes Are Necessary

- **Correct Class Loading**: By explicitly setting the classloader, you ensure that the classes manipulated by Javassist are loaded in the correct classloader context, avoiding issues with the child classloader set by scalatest.
  
- **Stability and Reliability**: These changes restore the functionality of the Mahout scalatest suite by ensuring that classes are found and loaded correctly, leading to stable and reliable test executions.

- **Best Practices**: Managing classloaders explicitly is a best practice in complex Java environments, especially when dealing with bytecode manipulation and testing frameworks that alter the classloader hierarchy.

- **Avoiding Subtle Bugs**: By addressing the class loading strategy, you avoid common pitfalls associated with Java class loading, particularly in environments with multiple classloaders, such as modular and microservice architectures.

Implementing these changes will help resolve the class loading issues and ensure that the system functions correctly in the test environment set by scalatest.

---

