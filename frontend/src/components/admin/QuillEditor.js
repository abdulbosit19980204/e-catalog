import React, { useRef, useEffect, useState, Component } from 'react';
import 'react-quill/dist/quill.snow.css';

// Error Boundary for QuillEditor
class QuillErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error) {
    // Only log in development
    if (process.env.NODE_ENV === 'development') {
      console.warn('QuillEditor error:', error);
    }
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback;
    }
    return this.props.children;
  }
}

// Lazy load ReactQuill to avoid SSR and findDOMNode issues
let ReactQuill = null;
let quillLoaded = false;

const loadReactQuill = () => {
  if (quillLoaded && ReactQuill) return ReactQuill;
  
  try {
    if (typeof window !== 'undefined') {
      // Load ReactQuill dynamically
      ReactQuill = require('react-quill').default;
      quillLoaded = true;
    }
  } catch (error) {
    if (process.env.NODE_ENV === 'development') {
      console.warn('Failed to load ReactQuill:', error);
    }
  }
  
  return ReactQuill;
};

const QuillEditor = ({ value, onChange, modules, className, style }) => {
  const quillRef = useRef(null);
  const containerRef = useRef(null);
  const [isClient, setIsClient] = useState(false);
  const [useFallback, setUseFallback] = useState(false);
  const [quillReady, setQuillReady] = useState(false);

  useEffect(() => {
    setIsClient(true);
    
    // Load ReactQuill on client side with delay to avoid findDOMNode issues
    const timer = setTimeout(() => {
      try {
        const loadedQuill = loadReactQuill();
        if (!loadedQuill) {
          setUseFallback(true);
        } else {
          setQuillReady(true);
        }
      } catch (err) {
        if (process.env.NODE_ENV === 'development') {
          console.warn('Error loading ReactQuill:', err);
        }
        setUseFallback(true);
      }
    }, 300);
    
    return () => clearTimeout(timer);
  }, []);

  // Fallback textarea component
  const TextareaFallback = () => (
    <div style={{ ...style, minHeight: '200px' }}>
      <textarea
        value={value || ''}
        onChange={(e) => onChange && onChange(e.target.value)}
        style={{
          width: '100%',
          minHeight: '180px',
          padding: '12px',
          border: '1px solid #dee2e6',
          borderRadius: '8px',
          outline: 'none',
          resize: 'vertical',
          fontFamily: 'inherit',
          fontSize: '14px',
          lineHeight: '1.5',
          transition: 'border-color 0.3s, box-shadow 0.3s',
        }}
        onFocus={(e) => {
          e.target.style.borderColor = '#007bff';
          e.target.style.boxShadow = '0 0 0 3px rgba(0, 123, 255, 0.1)';
        }}
        onBlur={(e) => {
          e.target.style.borderColor = '#dee2e6';
          e.target.style.boxShadow = 'none';
        }}
        placeholder="Description..."
      />
    </div>
  );

  // Use fallback if ReactQuill is not available
  if (!isClient || useFallback || !quillReady || !ReactQuill) {
    return <TextareaFallback />;
  }

  const QuillComponent = () => {
    try {
      // Wrap ReactQuill in a container to avoid findDOMNode issues
      return (
        <div ref={containerRef} style={style}>
          <ReactQuill
            ref={quillRef}
            theme="snow"
            value={value || ''}
            onChange={onChange}
            modules={modules}
            className={className}
            placeholder="Description..."
          />
        </div>
      );
    } catch (err) {
      if (process.env.NODE_ENV === 'development') {
        console.warn('ReactQuill render error, using fallback:', err);
      }
      setUseFallback(true);
      return <TextareaFallback />;
    }
  };

  return (
    <QuillErrorBoundary fallback={<TextareaFallback />}>
      <QuillComponent />
    </QuillErrorBoundary>
  );
};

QuillEditor.displayName = 'QuillEditor';

export default QuillEditor;
