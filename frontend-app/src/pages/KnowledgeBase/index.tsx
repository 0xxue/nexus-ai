import { useState, useEffect } from 'react';
import { listCollections, createCollection, deleteCollection, uploadDocument, listDocuments } from '../../api/kb';
import { Database, Upload, Trash2, FileText, Plus, Search } from 'lucide-react';

interface Collection {
  id: number;
  name: string;
  description: string;
  doc_count: number;
}

interface Document {
  id: number;
  filename: string;
  file_type: string;
  chunk_count: number;
  status: string;
}

export default function KnowledgeBasePage() {
  const [collections, setCollections] = useState<Collection[]>([]);
  const [selectedCollection, setSelectedCollection] = useState<Collection | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newName, setNewName] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    loadCollections();
  }, []);

  const loadCollections = async () => {
    try {
      const res: any = await listCollections();
      setCollections(res.collections || []);
    } catch {}
  };

  const loadDocuments = async (collection: Collection) => {
    setSelectedCollection(collection);
    try {
      const res: any = await listDocuments(collection.id);
      setDocuments(res.documents || []);
    } catch {}
  };

  const handleCreate = async () => {
    if (!newName.trim()) return;
    await createCollection(newName, newDesc);
    setNewName('');
    setNewDesc('');
    setShowCreateModal(false);
    loadCollections();
  };

  const handleDelete = async (id: number) => {
    if (!confirm('确认删除？')) return;
    await deleteCollection(id);
    if (selectedCollection?.id === id) {
      setSelectedCollection(null);
      setDocuments([]);
    }
    loadCollections();
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files?.length || !selectedCollection) return;
    setUploading(true);
    try {
      await uploadDocument(selectedCollection.id, e.target.files[0]);
      loadDocuments(selectedCollection);
    } catch (err) {
      alert('上传失败');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar: Collections */}
      <div className="w-72 bg-white border-r flex flex-col">
        <div className="p-4 border-b flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Database size={20} className="text-blue-600" />
            <h2 className="font-semibold">知识库</h2>
          </div>
          <button onClick={() => setShowCreateModal(true)} className="p-1.5 hover:bg-gray-100 rounded">
            <Plus size={18} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-2">
          {collections.map((c) => (
            <div
              key={c.id}
              onClick={() => loadDocuments(c)}
              className={`p-3 rounded-lg cursor-pointer mb-1 flex items-center justify-between ${
                selectedCollection?.id === c.id ? 'bg-blue-50 border border-blue-200' : 'hover:bg-gray-50'
              }`}
            >
              <div>
                <div className="font-medium text-sm">{c.name}</div>
                <div className="text-xs text-gray-400">{c.doc_count} 个文档</div>
              </div>
              <button onClick={(e) => { e.stopPropagation(); handleDelete(c.id); }} className="text-gray-300 hover:text-red-500">
                <Trash2 size={14} />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Main: Documents */}
      <div className="flex-1 flex flex-col">
        {selectedCollection ? (
          <>
            <div className="p-4 border-b bg-white flex items-center justify-between">
              <div>
                <h3 className="font-semibold">{selectedCollection.name}</h3>
                <p className="text-sm text-gray-500">{selectedCollection.description}</p>
              </div>
              <label className={`flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg cursor-pointer hover:bg-blue-700 ${uploading ? 'opacity-50' : ''}`}>
                <Upload size={16} />
                {uploading ? '上传中...' : '上传文档'}
                <input type="file" className="hidden" onChange={handleUpload} accept=".pdf,.docx,.xlsx,.csv,.txt,.md" disabled={uploading} />
              </label>
            </div>

            <div className="flex-1 overflow-y-auto p-4">
              {documents.length === 0 ? (
                <div className="text-center text-gray-400 mt-20">
                  <FileText size={48} className="mx-auto mb-4" />
                  <p>暂无文档，点击上方按钮上传</p>
                  <p className="text-xs mt-1">支持 PDF / Word / Excel / TXT</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {documents.map((doc) => (
                    <div key={doc.id} className="flex items-center justify-between p-3 bg-white rounded-lg border">
                      <div className="flex items-center gap-3">
                        <FileText size={20} className="text-gray-400" />
                        <div>
                          <div className="font-medium text-sm">{doc.filename}</div>
                          <div className="text-xs text-gray-400">{doc.chunk_count} 个分块 · {doc.status}</div>
                        </div>
                      </div>
                      <span className={`text-xs px-2 py-0.5 rounded ${
                        doc.status === 'ready' ? 'bg-green-50 text-green-600' :
                        doc.status === 'processing' ? 'bg-yellow-50 text-yellow-600' :
                        'bg-red-50 text-red-600'
                      }`}>
                        {doc.status}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-400">
            <div className="text-center">
              <Search size={48} className="mx-auto mb-4" />
              <p>选择或创建一个知识库</p>
            </div>
          </div>
        )}
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-96">
            <h3 className="text-lg font-semibold mb-4">创建知识库</h3>
            <input
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              placeholder="知识库名称"
              className="w-full border rounded-lg px-3 py-2 mb-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <textarea
              value={newDesc}
              onChange={(e) => setNewDesc(e.target.value)}
              placeholder="描述（可选）"
              className="w-full border rounded-lg px-3 py-2 mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={2}
            />
            <div className="flex gap-2 justify-end">
              <button onClick={() => setShowCreateModal(false)} className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg">取消</button>
              <button onClick={handleCreate} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">创建</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
