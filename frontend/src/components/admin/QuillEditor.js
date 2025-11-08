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
  modules = DEFAULT_MODULES,
  className = "",
  style,
  placeholder = "Description...",
}) => {
  const containerRef = useRef(null);
  const editorRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current || typeof window === "undefined") {
      return undefined;
    }

    const quill = new Quill(containerRef.current, {
      theme: "snow",
      modules,
      placeholder,
    });

    if (value) {
      quill.clipboard.dangerouslyPasteHTML(value);
    }

    const handleChange = () => {
      const html = sanitizeEmpty(quill.root.innerHTML);
      if (onChange) {
        onChange(html);
      }
    };

    quill.on("text-change", handleChange);
    editorRef.current = quill;

    return () => {
      quill.off("text-change", handleChange);
      // Dispose quill instance
      if (containerRef.current) {
        containerRef.current.innerHTML = "";
      }
    };
  }, [modules, onChange, placeholder]);

  useEffect(() => {
    if (!editorRef.current) return;
    const quill = editorRef.current;
    const current = sanitizeEmpty(quill.root.innerHTML);
    const next = sanitizeEmpty(value);
    if (next !== undefined && next !== current) {
      const sel = quill.getSelection();
      quill.clipboard.dangerouslyPasteHTML(next || "");
      if (sel) {
        quill.setSelection(sel);
      }
    }
  }, [value]);

  return (
    <div
      className={`quill-editor-container ${className}`.trim()}
      style={{ minHeight: 220, ...style }}
    >
      <div ref={containerRef} />
    </div>
  );
};

export default QuillEditor;
