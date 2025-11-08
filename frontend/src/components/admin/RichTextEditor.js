import React, { useCallback, useMemo } from "react";
import { CKEditor } from "@ckeditor/ckeditor5-react";
import ClassicEditor from "@ckeditor/ckeditor5-build-classic";

const editorToolbar = [
  "heading",
  "|",
  "bold",
  "italic",
  "underline",
  "link",
  "bulletedList",
  "numberedList",
  "blockQuote",
  "|",
  "undo",
  "redo",
];

const RichTextEditor = ({
  value,
  onChange,
  className,
  placeholder = "Description...",
}) => {
  const data = value || "";

  const editorConfig = useMemo(
    () => ({
      toolbar: editorToolbar,
      placeholder,
    }),
    [placeholder]
  );

  const handleChange = useCallback(
    (_, editor) => {
      if (onChange) {
        onChange(editor.getData());
      }
    },
    [onChange]
  );

  const handleReady = useCallback((editor) => {
    const editable = editor.editing.view;
    editable.change((writer) => {
      writer.setStyle("min-height", "220px", editable.document.getRoot());
    });
  }, []);

  return (
    <div className={`rich-text-editor ${className || ""}`}>
      <CKEditor
        editor={ClassicEditor}
        data={data}
        config={editorConfig}
        onChange={handleChange}
        onReady={handleReady}
      />
    </div>
  );
};

export default RichTextEditor;
