import React, { useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  DndContext,
  closestCenter,
  PointerSensor,
  useSensor,
  useSensors,
} from "@dnd-kit/core";
import {
  arrayMove,
  SortableContext,
  useSortable,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";

function SortableItem({ id, children }) {
  const { attributes, listeners, setNodeRef, transform, transition } =
    useSortable({ id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  return (
    <div ref={setNodeRef} style={style} {...attributes} {...listeners}>
      {children}
    </div>
  );
}

export default function StrategiesTab() {
  const [strategies, setStrategies] = useState([]);
  const [editingIndex, setEditingIndex] = useState(null);
  const [editedText, setEditedText] = useState("");
  const [saving, setSaving] = useState(false);

  const fetchStrategies = async () => {
    const res = await fetch("/api/strategies");
    const data = await res.json();

    const enriched = data.map((item, i) => ({
      id: `${i}-${item.context?.slice(0, 5) || "item"}`,
      ...item,
    }));

    setStrategies(enriched);
  };

  const saveEdited = async (index) => {
    setSaving(true);
    await fetch("/api/strategies/update", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ index, improved: editedText }),
    });
    setEditingIndex(null);
    setEditedText("");
    await fetchStrategies();
    setSaving(false);
  };

  const saveOrder = async (newList) => {
    const cleaned = newList.map(({ id, ...rest }) => rest);
    await fetch("/api/strategies/reorder", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(cleaned),
    });
    setStrategies(newList);
  };

  const sensors = useSensors(useSensor(PointerSensor));

  const handleDragEnd = (event) => {
    const { active, over } = event;
    if (active.id !== over?.id) {
      const oldIndex = strategies.findIndex((s) => s.id === active.id);
      const newIndex = strategies.findIndex((s) => s.id === over?.id);
      const newList = arrayMove(strategies, oldIndex, newIndex);
      saveOrder(newList);
    }
  };

  useEffect(() => {
    fetchStrategies();
  }, []);

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">📈 Стратегії</h2>
      <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
        <SortableContext items={strategies.map((s) => s.id)} strategy={verticalListSortingStrategy}>
          {strategies.map((item, index) => (
            <SortableItem key={item.id} id={item.id}>
              <Card className="border border-muted">
                <CardContent className="space-y-3 py-4">
                  <p className="text-sm">
                    <span className="font-semibold">Контекст:</span>
                    <br />
                    <span className="whitespace-pre-wrap">{item.context}</span>
                  </p>

                  <p className="text-sm">
                    <span className="font-semibold">Було (🤖):</span>
                    <br />
                    <span className="text-red-600 whitespace-pre-wrap">{item.original}</span>
                  </p>

                  <p className="text-sm">
                    <span className="font-semibold">Стало:</span>
                    <br />
                    {editingIndex === index ? (
                      <>
                        <Textarea
                          rows={4}
                          value={editedText}
                          onChange={(e) => setEditedText(e.target.value)}
                          className="mt-2"
                        />
                        <div className="flex gap-2 mt-2">
                          <Button
                            size="sm"
                            onClick={() => saveEdited(index)}
                            disabled={saving || !editedText.trim()}
                          >
                            Зберегти
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => {
                              setEditingIndex(null);
                              setEditedText("");
                            }}
                          >
                            Скасувати
                          </Button>
                        </div>
                      </>
                    ) : (
                      <div className="flex justify-between items-center mt-1">
                        <span className="whitespace-pre-wrap">{item.improved || "—"}</span>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            setEditingIndex(index);
                            setEditedText(item.improved || "");
                          }}
                        >
                          Редагувати
                        </Button>
                      </div>
                    )}
                  </p>

                  {item.strategy && (
                    <p className="text-muted-foreground text-sm">
                      <span className="font-semibold">Стратегія:</span>
                      <br />
                      {item.strategy}
                    </p>
                  )}

                  {item.feedback?.length > 0 && (
                    <div className="bg-muted px-3 py-2 rounded text-sm">
                      <span className="font-medium">Коментарі:</span>
                      <ul className="list-disc ml-5 mt-1">
                        {item.feedback.map((f, i) => (
                          <li key={i}>{f}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </CardContent>
              </Card>
            </SortableItem>
          ))}
        </SortableContext>
      </DndContext>
    </div>
  );
}
