import React, { useEffect, useRef } from "react";
import Quill from "quill";
import "quill/dist/quill.snow.css";

const DEFAULT_MODULES = {
  toolbar: [
    [{ header: [1, 2, 3, false] }],
    ["bold", "italic", "underline", "strike"],
    [{ list: "ordered" }, { list: "bullet" }],
    [{ align: [] }],
    ["link", "image"],
    ["clean"],
  ],
};

const sanitizeEmpty = (html) => {
  if (!html) return "";
  return html === "<p><br></p>" ? "" : html;
};

const QuillEditor = ({
  value,
  onChange,
  modules,
  className = "",
  style,
  placeholder = "Description...",
}) => {
  const containerRef = useRef(null);
  const editorRef = useRef(null);
  const modulesRef = useRef(DEFAULT_MODULES);
  const onChangeRef = useRef(onChange);
  const isInternalChange = useRef(false);

  useEffect(() => {
    modulesRef.current = modules || DEFAULT_MODULES;
  }, [modules]);

  useEffect(() => {
    onChangeRef.current = onChange;
  }, [onChange]);

  useEffect(() => {
    if (!containerRef.current || editorRef.current || typeof window === "undefined") {
      return undefined;
    }

    const hostElement = containerRef.current;
    
    // Clear and create editor container
    hostElement.innerHTML = "<div></div>";
    const editArea = hostElement.firstChild;

    const quill = new Quill(editArea, {
      theme: "snow",
      modules: modulesRef.current,
      placeholder,
    });

    if (value) {
      quill.clipboard.dangerouslyPasteHTML(value);
    }

    const handleChange = () => {
      if (isInternalChange.current) return;
      
      const html = sanitizeEmpty(quill.root.innerHTML);
      if (onChangeRef.current) {
        onChangeRef.current(html);
      }
    };

    quill.on("text-change", handleChange);
    editorRef.current = quill;

    return () => {
      quill.off("text-change", handleChange);
      editorRef.current = null;
      hostElement.innerHTML = "";
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [placeholder]);

  useEffect(() => {
    const quill = editorRef.current;
    if (!quill) return;

    const current = sanitizeEmpty(quill.root.innerHTML);
    const next = sanitizeEmpty(value);

    // Only update if external value is meaningfully different from editor content
    if (next !== undefined && next !== current) {
      isInternalChange.current = true;
      const selection = quill.getSelection();
      quill.clipboard.dangerouslyPasteHTML(next || "");
      if (selection) {
        quill.setSelection(selection);
      }
      isInternalChange.current = false;
    }
  }, [value]);

  return (
    <div
      className={`quill-editor-container ${className}`.trim()}
      style={{ 
        minHeight: 250, 
        display: 'flex', 
        flexDirection: 'column',
        border: '1px solid var(--border-color)',
        borderRadius: '10px',
        overflow: 'hidden',
        background: 'var(--bg-main)',
        ...style 
      }}
    >
      <div ref={containerRef} style={{ flex: 1, display: 'flex', flexDirection: 'column' }} />
    </div>
  );
};

export default QuillEditor;
