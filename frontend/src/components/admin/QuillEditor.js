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

    const quill = new Quill(containerRef.current, {
      theme: "snow",
      modules: modulesRef.current,
      placeholder,
    });

    if (value) {
      quill.clipboard.dangerouslyPasteHTML(value);
    }

    const handleChange = () => {
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
      if (containerRef.current) {
        containerRef.current.innerHTML = "";
      }
    };
  }, [placeholder]);

  useEffect(() => {
    const quill = editorRef.current;
    if (!quill) return;

    const current = sanitizeEmpty(quill.root.innerHTML);
    const next = sanitizeEmpty(value);

    if (next !== undefined && next !== current) {
      const selection = quill.getSelection();
      quill.clipboard.dangerouslyPasteHTML(next || "");
      if (selection) {
        quill.setSelection(selection);
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
