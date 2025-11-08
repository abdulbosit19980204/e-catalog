import React, { useEffect, useMemo } from "react";
import { useEditor, EditorContent } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import Underline from "@tiptap/extension-underline";
import Link from "@tiptap/extension-link";
import Placeholder from "@tiptap/extension-placeholder";

const TIPTAP_EXTENSIONS = [
  StarterKit.configure({
    heading: {
      levels: [1, 2, 3],
    },
  }),
  Underline,
  Link.configure({
    openOnClick: true,
    autolink: true,
    linkOnPaste: true,
  }),
];

const RichTextEditor = ({ value, onChange, className, placeholder = "Description..." }) => {
  const extensions = useMemo(
    () => [
      ...TIPTAP_EXTENSIONS,
      Placeholder.configure({
        placeholder,
      }),
    ],
    [placeholder]
  );

  const editor = useEditor({
    extensions,
    content: value || "",
    editorProps: {
      attributes: {
        class: "tiptap-editor",
      },
    },
    onUpdate: ({ editor }) => {
      if (!onChange) return;
      const html = editor.getHTML();
      if (html !== value) {
        onChange(html);
      }
    },
  });

  useEffect(() => {
    if (!editor) return;
    const html = value || "";
    if (html !== editor.getHTML()) {
      editor.commands.setContent(html, false);
    }
  }, [value, editor]);

  if (!editor) {
    return null;
  }

  const setLink = () => {
    if (!editor) return;
    const previous = editor.getAttributes("link").href || "";
    const url = window.prompt("Link manzilini kiriting", previous);
    if (url === null) {
      return;
    }
    if (url.trim() === "") {
      editor.chain().focus().unsetLink().run();
      return;
    }
    editor.chain().focus().extendMarkRange("link").setLink({ href: url.trim() }).run();
  };

  const buttons = [
    {
      label: "B",
      title: "Bold",
      isActive: editor.isActive("bold"),
      disabled: !editor.can().chain().focus().toggleBold().run(),
      action: () => editor.chain().focus().toggleBold().run(),
    },
    {
      label: "I",
      title: "Italic",
      isActive: editor.isActive("italic"),
      disabled: !editor.can().chain().focus().toggleItalic().run(),
      action: () => editor.chain().focus().toggleItalic().run(),
    },
    {
      label: "U",
      title: "Underline",
      isActive: editor.isActive("underline"),
      disabled: !editor.can().chain().focus().toggleUnderline().run(),
      action: () => editor.chain().focus().toggleUnderline().run(),
    },
    {
      label: "•",
      title: "Bullet list",
      isActive: editor.isActive("bulletList"),
      disabled: !editor.can().chain().focus().toggleBulletList().run(),
      action: () => editor.chain().focus().toggleBulletList().run(),
    },
    {
      label: "1.",
      title: "Ordered list",
      isActive: editor.isActive("orderedList"),
      disabled: !editor.can().chain().focus().toggleOrderedList().run(),
      action: () => editor.chain().focus().toggleOrderedList().run(),
    },
    {
      label: "“”",
      title: "Blockquote",
      isActive: editor.isActive("blockquote"),
      disabled: !editor.can().chain().focus().toggleBlockquote().run(),
      action: () => editor.chain().focus().toggleBlockquote().run(),
    },
    {
      label: "H2",
      title: "Heading 2",
      isActive: editor.isActive("heading", { level: 2 }),
      disabled: !editor.can().chain().focus().toggleHeading({ level: 2 }).run(),
      action: () => editor.chain().focus().toggleHeading({ level: 2 }).run(),
    },
    {
      label: "↩",
      title: "Undo",
      disabled: !editor.can().chain().focus().undo().run(),
      action: () => editor.chain().focus().undo().run(),
    },
    {
      label: "↪",
      title: "Redo",
      disabled: !editor.can().chain().focus().redo().run(),
      action: () => editor.chain().focus().redo().run(),
    },
    {
      label: "🔗",
      title: "Link",
      isActive: editor.isActive("link"),
      disabled: false,
      action: setLink,
    },
    {
      label: "✕",
      title: "Remove link",
      disabled: !editor.isActive("link"),
      action: () => editor.chain().focus().unsetLink().run(),
    },
  ];

  return (
    <div className={`rich-text-editor ${className || ""}`}>
      <div className="rich-text-toolbar">
        {buttons.map(({ label, title, action, disabled, isActive }, index) => (
          <button
            key={title + index}
            type="button"
            className={isActive ? "is-active" : ""}
            disabled={disabled}
            onMouseDown={(event) => event.preventDefault()}
            onClick={() => action && action()}
            title={title}
          >
            {label}
          </button>
        ))}
      </div>
      <EditorContent editor={editor} />
    </div>
  );
};

export default RichTextEditor;
