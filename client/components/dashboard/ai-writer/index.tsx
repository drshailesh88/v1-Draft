'use client';

import DashboardLayout from '@/components/layout';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { api, apiCall } from '@/lib/api';
import { User } from '@supabase/supabase-js';
import { useState, useEffect } from 'react';
import {
  HiOutlinePencilSquare,
  HiOutlineDocumentPlus,
  HiOutlineSparkles,
  HiOutlineArrowDownTray,
  HiOutlineTrash,
  HiOutlinePencil,
  HiOutlineCheck,
  HiOutlineXMark,
} from 'react-icons/hi2';

interface Props {
  user: User | null | undefined;
  userDetails: { [x: string]: any } | null;
}

interface Project {
  id: string;
  name: string;
  description: string;
  sections: Section[];
  created_at: string;
  updated_at: string;
}

interface Section {
  id: string;
  type: string;
  content: string;
  generated_at: string;
}

const SECTION_TYPES = [
  { value: 'abstract', label: 'Abstract' },
  { value: 'introduction', label: 'Introduction' },
  { value: 'literature_review', label: 'Literature Review' },
  { value: 'methods', label: 'Methods' },
  { value: 'results', label: 'Results' },
  { value: 'discussion', label: 'Discussion' },
  { value: 'conclusion', label: 'Conclusion' },
  { value: 'acknowledgments', label: 'Acknowledgments' },
];

const EXPORT_FORMATS = [
  { value: 'latex', label: 'LaTeX (.tex)' },
  { value: 'markdown', label: 'Markdown (.md)' },
  { value: 'docx', label: 'Word (.docx)' },
];

export default function AIWriter(props: Props) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [generating, setGenerating] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Form states
  const [newProjectName, setNewProjectName] = useState<string>('');
  const [newProjectDescription, setNewProjectDescription] = useState<string>('');
  const [showNewProject, setShowNewProject] = useState<boolean>(false);

  // Section generation states
  const [sectionType, setSectionType] = useState<string>('abstract');
  const [context, setContext] = useState<string>('');
  const [generatedContent, setGeneratedContent] = useState<string>('');
  const [editingContent, setEditingContent] = useState<boolean>(false);
  const [editedContent, setEditedContent] = useState<string>('');

  // Load projects on mount
  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiCall<{ projects: Project[] }>(api.aiWriter.projects, {
        method: 'GET',
      });
      setProjects(response.projects || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  const createProject = async () => {
    if (!newProjectName.trim()) {
      setError('Please enter a project name');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const response = await apiCall<Project>(api.aiWriter.projects, {
        method: 'POST',
        body: JSON.stringify({
          name: newProjectName,
          description: newProjectDescription,
        }),
      });
      setProjects([response, ...projects]);
      setSelectedProject(response);
      setNewProjectName('');
      setNewProjectDescription('');
      setShowNewProject(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create project');
    } finally {
      setLoading(false);
    }
  };

  const deleteProject = async (projectId: string) => {
    if (!confirm('Are you sure you want to delete this project?')) return;

    setLoading(true);
    try {
      await apiCall(api.aiWriter.project(projectId), {
        method: 'DELETE',
      });
      setProjects(projects.filter((p) => p.id !== projectId));
      if (selectedProject?.id === projectId) {
        setSelectedProject(null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete project');
    } finally {
      setLoading(false);
    }
  };

  const generateSection = async () => {
    if (!selectedProject) {
      setError('Please select or create a project first');
      return;
    }

    if (!context.trim()) {
      setError('Please provide context for the section generation');
      return;
    }

    setGenerating(true);
    setError(null);
    setGeneratedContent('');

    try {
      const response = await apiCall<{ content: string; section_id: string }>(
        api.aiWriter.generateSection(selectedProject.id),
        {
          method: 'POST',
          body: JSON.stringify({
            section_type: sectionType,
            context: context,
            existing_sections: selectedProject.sections,
          }),
        }
      );
      setGeneratedContent(response.content);
      setEditedContent(response.content);

      // Refresh project to get updated sections
      const updatedProject = await apiCall<Project>(
        api.aiWriter.project(selectedProject.id),
        { method: 'GET' }
      );
      setSelectedProject(updatedProject);
      setProjects(projects.map((p) => (p.id === updatedProject.id ? updatedProject : p)));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate section');
    } finally {
      setGenerating(false);
    }
  };

  const handleExport = async (format: string) => {
    if (!selectedProject) return;

    try {
      const response = await fetch(
        `${api.aiWriter.export(selectedProject.id)}?format=${format}`,
        { method: 'GET' }
      );

      if (!response.ok) throw new Error('Export failed');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${selectedProject.name}.${format === 'latex' ? 'tex' : format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Export failed');
    }
  };

  const saveEditedContent = () => {
    setGeneratedContent(editedContent);
    setEditingContent(false);
  };

  return (
    <DashboardLayout
      user={props.user}
      userDetails={props.userDetails}
      title="AI Writer"
      description="AI-powered academic writing assistant"
    >
      <div className="mx-auto max-w-7xl space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-zinc-950 dark:bg-white">
              <HiOutlinePencilSquare className="h-6 w-6 text-white dark:text-zinc-950" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-zinc-950 dark:text-white">AI Writer</h1>
              <p className="text-sm text-zinc-500 dark:text-zinc-400">
                Generate academic paper sections with AI assistance
              </p>
            </div>
          </div>
        </div>

        {error && (
          <div className="rounded-lg bg-red-50 p-4 text-sm text-red-600 dark:bg-red-900/20 dark:text-red-400">
            {error}
          </div>
        )}

        <div className="grid gap-6 lg:grid-cols-3">
          {/* Projects Panel */}
          <Card className="lg:col-span-1">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">Projects</CardTitle>
                <Button
                  size="sm"
                  variant={showNewProject ? 'outline' : 'default'}
                  onClick={() => setShowNewProject(!showNewProject)}
                >
                  {showNewProject ? (
                    <HiOutlineXMark className="h-4 w-4" />
                  ) : (
                    <HiOutlineDocumentPlus className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* New Project Form */}
              {showNewProject && (
                <div className="space-y-3 rounded-lg border border-zinc-200 p-3 dark:border-zinc-800">
                  <Input
                    placeholder="Project name"
                    value={newProjectName}
                    onChange={(e) => setNewProjectName(e.target.value)}
                  />
                  <Textarea
                    placeholder="Description (optional)"
                    value={newProjectDescription}
                    onChange={(e) => setNewProjectDescription(e.target.value)}
                    className="min-h-[60px]"
                  />
                  <Button
                    className="w-full"
                    onClick={createProject}
                    disabled={loading}
                  >
                    Create Project
                  </Button>
                </div>
              )}

              {/* Project List */}
              <div className="max-h-[400px] space-y-2 overflow-y-auto">
                {loading && projects.length === 0 ? (
                  <div className="py-8 text-center text-zinc-500">Loading...</div>
                ) : projects.length === 0 ? (
                  <div className="py-8 text-center text-zinc-500">
                    No projects yet. Create one to get started.
                  </div>
                ) : (
                  projects.map((project) => (
                    <div
                      key={project.id}
                      className={`cursor-pointer rounded-lg border p-3 transition-colors ${
                        selectedProject?.id === project.id
                          ? 'border-zinc-950 bg-zinc-50 dark:border-white dark:bg-zinc-900'
                          : 'border-zinc-200 hover:bg-zinc-50 dark:border-zinc-800 dark:hover:bg-zinc-900'
                      }`}
                      onClick={() => setSelectedProject(project)}
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <h3 className="font-medium text-zinc-950 dark:text-white">
                            {project.name}
                          </h3>
                          {project.description && (
                            <p className="mt-1 text-xs text-zinc-500 line-clamp-2">
                              {project.description}
                            </p>
                          )}
                          <p className="mt-1 text-xs text-zinc-400">
                            {project.sections?.length || 0} sections
                          </p>
                        </div>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={(e) => {
                            e.stopPropagation();
                            deleteProject(project.id);
                          }}
                        >
                          <HiOutlineTrash className="h-4 w-4 text-red-500" />
                        </Button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>

          {/* Main Content Panel */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <HiOutlineSparkles className="h-5 w-5" />
                Generate Section
              </CardTitle>
              <CardDescription>
                {selectedProject
                  ? `Working on: ${selectedProject.name}`
                  : 'Select a project to start generating content'}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {!selectedProject ? (
                <div className="flex h-[300px] flex-col items-center justify-center text-center text-zinc-500">
                  <HiOutlinePencilSquare className="mb-4 h-16 w-16 opacity-20" />
                  <p>Select a project from the list or create a new one</p>
                </div>
              ) : (
                <Tabs defaultValue="generate" className="w-full">
                  <TabsList className="w-full">
                    <TabsTrigger value="generate" className="flex-1">
                      Generate
                    </TabsTrigger>
                    <TabsTrigger value="sections" className="flex-1">
                      Sections ({selectedProject.sections?.length || 0})
                    </TabsTrigger>
                    <TabsTrigger value="export" className="flex-1">
                      Export
                    </TabsTrigger>
                  </TabsList>

                  <TabsContent value="generate" className="space-y-4">
                    {/* Section Type Selector */}
                    <div className="space-y-2">
                      <Label>Section Type</Label>
                      <Select value={sectionType} onValueChange={setSectionType}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select section type" />
                        </SelectTrigger>
                        <SelectContent>
                          {SECTION_TYPES.map((type) => (
                            <SelectItem key={type.value} value={type.value}>
                              {type.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    {/* Context Input */}
                    <div className="space-y-2">
                      <Label>Context / Instructions</Label>
                      <Textarea
                        placeholder="Provide context for the section. Include research topic, key findings, methodology details, or any specific requirements..."
                        className="min-h-[120px]"
                        value={context}
                        onChange={(e) => setContext(e.target.value)}
                      />
                    </div>

                    {/* Generate Button */}
                    <Button
                      className="w-full"
                      onClick={generateSection}
                      disabled={generating || !context.trim()}
                    >
                      {generating ? (
                        <>
                          <span className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                          Generating...
                        </>
                      ) : (
                        <>
                          <HiOutlineSparkles className="mr-2 h-4 w-4" />
                          Generate {SECTION_TYPES.find((t) => t.value === sectionType)?.label}
                        </>
                      )}
                    </Button>

                    {/* Generated Content */}
                    {generatedContent && (
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <Label>Generated Content</Label>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => {
                              if (editingContent) {
                                saveEditedContent();
                              } else {
                                setEditedContent(generatedContent);
                                setEditingContent(true);
                              }
                            }}
                          >
                            {editingContent ? (
                              <>
                                <HiOutlineCheck className="mr-1 h-4 w-4" />
                                Save
                              </>
                            ) : (
                              <>
                                <HiOutlinePencil className="mr-1 h-4 w-4" />
                                Edit
                              </>
                            )}
                          </Button>
                        </div>
                        {editingContent ? (
                          <Textarea
                            className="min-h-[200px] font-mono text-sm"
                            value={editedContent}
                            onChange={(e) => setEditedContent(e.target.value)}
                          />
                        ) : (
                          <div className="max-h-[300px] overflow-y-auto rounded-lg border border-zinc-200 bg-zinc-50 p-4 dark:border-zinc-800 dark:bg-zinc-900">
                            <pre className="whitespace-pre-wrap font-sans text-sm text-zinc-700 dark:text-zinc-300">
                              {generatedContent}
                            </pre>
                          </div>
                        )}
                      </div>
                    )}
                  </TabsContent>

                  <TabsContent value="sections" className="space-y-4">
                    {selectedProject.sections?.length === 0 ? (
                      <div className="py-8 text-center text-zinc-500">
                        No sections generated yet. Use the Generate tab to create content.
                      </div>
                    ) : (
                      <div className="space-y-4">
                        {selectedProject.sections?.map((section, index) => (
                          <div
                            key={section.id || index}
                            className="rounded-lg border border-zinc-200 p-4 dark:border-zinc-800"
                          >
                            <div className="mb-2 flex items-center justify-between">
                              <Badge variant="secondary">
                                {SECTION_TYPES.find((t) => t.value === section.type)?.label ||
                                  section.type}
                              </Badge>
                              <span className="text-xs text-zinc-500">
                                {new Date(section.generated_at).toLocaleDateString()}
                              </span>
                            </div>
                            <p className="line-clamp-4 text-sm text-zinc-700 dark:text-zinc-300">
                              {section.content}
                            </p>
                          </div>
                        ))}
                      </div>
                    )}
                  </TabsContent>

                  <TabsContent value="export" className="space-y-4">
                    <div className="rounded-lg border border-zinc-200 p-6 dark:border-zinc-800">
                      <h3 className="mb-4 text-lg font-medium">Export Project</h3>
                      <p className="mb-6 text-sm text-zinc-500">
                        Download your project in various formats for use in academic writing tools.
                      </p>
                      <div className="grid gap-3 sm:grid-cols-3">
                        {EXPORT_FORMATS.map((format) => (
                          <Button
                            key={format.value}
                            variant="outline"
                            className="h-auto flex-col py-4"
                            onClick={() => handleExport(format.value)}
                            disabled={!selectedProject.sections?.length}
                          >
                            <HiOutlineArrowDownTray className="mb-2 h-6 w-6" />
                            <span>{format.label}</span>
                          </Button>
                        ))}
                      </div>
                      {!selectedProject.sections?.length && (
                        <p className="mt-4 text-center text-sm text-zinc-500">
                          Generate some sections before exporting.
                        </p>
                      )}
                    </div>
                  </TabsContent>
                </Tabs>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}
