"use client";

import { useEffect, useState, useSyncExternalStore } from "react";

import { useRouter } from "next/navigation";

import { getHospitalAuth, clearHospitalAuth } from "@/lib/hospital-auth";
import {
  getHospitalNotifications,
  getHospitalUnreadCount,
  markNotificationAsRead,
  markAllNotificationsAsRead,
  type HospitalNotification,
} from "@/lib/hospital-notification-api";

const emptySubscribe = () => {
  return () => {};
};

const getServerSnapshot = () => false;

const getClientSnapshot = () => true;

export default function HospitalDashboardPage() {
  const router = useRouter();

  const [notifications, setNotifications] = useState<
    HospitalNotification[] | null
  >(null);

  const [unreadCount, setUnreadCount] = useState(0);

  const [notificationOpen, setNotificationOpen] = useState(false);

  /*
   * This becomes true only after the browser
   * takes over from the server-rendered page.
   */
  const mounted = useSyncExternalStore(
    emptySubscribe,
    getClientSnapshot,
    getServerSnapshot,
  );

  const auth = mounted ? getHospitalAuth() : null;

  useEffect(() => {
    if (!mounted) {
      return;
    }

    if (!auth?.accessToken) {
      router.replace("/hospital/login");
    }
  }, [mounted, auth?.accessToken, router]);

  // const loadNotifications = async () => {
  //   try {
  //     const [notificationsResponse, unreadResponse] = await Promise.all([
  //       getHospitalNotifications(),
  //       getHospitalUnreadCount(),
  //     ]);

  //     setNotifications(notificationsResponse.data);

  //     setUnreadCount(unreadResponse.unread_count);
  //   } catch (error) {
  //     console.error("Failed to load hospital notifications:", error);

  //     // Don't leave the UI stuck in loading state.
  //     setNotifications([]);
  //   }
  // };

  useEffect(() => {
    if (!mounted || !auth?.accessToken) {
      return;
    }

    let cancelled = false;

    const fetchNotifications = async () => {
      try {
        const [notificationsResponse, unreadResponse] = await Promise.all([
          getHospitalNotifications(),
          getHospitalUnreadCount(),
        ]);

        if (cancelled) {
          return;
        }

        setNotifications(notificationsResponse.data);

        setUnreadCount(unreadResponse.unread_count);
      } catch (error) {
        if (cancelled) {
          return;
        }

        console.error("Failed to load hospital notifications:", error);

        setNotifications([]);
      }
    };

    void fetchNotifications();

    return () => {
      cancelled = true;
    };
  }, [mounted, auth?.accessToken]);

  const handleNotificationClick = async (
    notification: HospitalNotification,
  ) => {
    try {
      if (!notification.is_read) {
        await markNotificationAsRead(notification.id);

        setNotifications((current) => {
          if (current === null) {
            return current;
          }

          return current.map((item) =>
            item.id === notification.id
              ? {
                  ...item,
                  is_read: true,
                  read_at: new Date().toISOString(),
                }
              : item,
          );
        });

        setUnreadCount((current) => Math.max(0, current - 1));
      }

      if (notification.appointment_request_id) {
        // We'll connect this to the
        // appointment detail page next.
        console.log(
          "Appointment request:",
          notification.appointment_request_id,
        );
      }
    } catch (error) {
      console.error("Failed to mark notification as read:", error);
    }
  };

  useEffect(() => {
    if (!mounted || !auth?.accessToken || !auth?.hospitalId) {
      return;
    }

    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";

    const wsHost = process.env.NEXT_PUBLIC_API_WS_URL || "127.0.0.1:8000";

    const websocketUrl = `${protocol}//${wsHost}/ai/hospital/ws/${auth.hospitalId}`;

    console.log("Connecting hospital WebSocket:", websocketUrl);

    const socket = new WebSocket(websocketUrl);

    socket.onopen = () => {
      console.log("Hospital WebSocket connected:", auth.hospitalId);
    };

    socket.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);

        console.log("Hospital WebSocket message:", payload);

        if (payload?.event !== "appointment_request_created") {
          return;
        }

        const data = payload.data;

        if (!data?.notification_id) {
          return;
        }

        const newNotification: HospitalNotification = {
          id: data.notification_id,
          hospital_id: data.hospital_id,
          appointment_request_id: data.appointment_request_id,
          type: data.type || "appointment_request_created",
          title: data.title || "New Appointment Request",
          message: data.message || "",
          is_read: false,
          created_at: data.created_at || new Date().toISOString(),
          read_at: null,
        };

        setNotifications((current) => {
          if (current === null) {
            return [newNotification];
          }

          const alreadyExists = current.some(
            (notification) => notification.id === newNotification.id,
          );

          if (alreadyExists) {
            return current;
          }

          return [newNotification, ...current];
        });

        setUnreadCount((current) => current + 1);

        // Optional:
        // automatically open notification panel
        setNotificationOpen(true);
      } catch (error) {
        console.error("Failed to process hospital WebSocket message:", error);
      }
    };

    socket.onerror = (error) => {
      console.error("Hospital WebSocket error:", error);
    };

    socket.onclose = (event) => {
      console.log("Hospital WebSocket disconnected:", event.code, event.reason);
    };

    return () => {
      console.log("Closing hospital WebSocket");

      socket.close();
    };
  }, [mounted, auth?.accessToken, auth?.hospitalId]);

  const handleMarkAllRead = async () => {
    try {
      await markAllNotificationsAsRead();

      setNotifications((current) => {
        if (current === null) {
          return current;
        }

        return current.map((notification) => ({
          ...notification,
          is_read: true,
          read_at: notification.read_at ?? new Date().toISOString(),
        }));
      });

      setUnreadCount(0);
    } catch (error) {
      console.error("Failed to mark notifications as read:", error);
    }
  };

  /*
   * Don't render dashboard while
   * authentication is being resolved.
   */
  if (!mounted) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#050b14] text-white">
        <div className="text-sm text-white/40">Loading hospital portal...</div>
      </div>
    );
  }

  if (!auth?.accessToken) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#050b14] text-white">
        <div className="text-sm text-white/40">Redirecting to login...</div>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-[#050b14] text-white">
      {/* HEADER */}

      <header className="border-b border-white/10 bg-[#07111d]">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-8 py-5">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.3em] text-cyan-400">
              LIGHTNINGQ
            </div>

            <h1 className="mt-1 text-2xl font-semibold">{auth.hospitalName}</h1>

            <div className="mt-1 text-sm text-white/40">Hospital Portal</div>
          </div>

          <div className="flex items-center gap-6">
            <div className="text-right">
              <div className="font-medium text-white">{auth.userName}</div>

              <div className="text-sm text-cyan-400">{auth.roleName}</div>
            </div>

            {/* Notification */}

            <div className="relative">
              <button
                type="button"
                onClick={() => setNotificationOpen((current) => !current)}
                className="relative flex h-11 w-11 items-center justify-center rounded-xl border border-white/10 bg-white/[0.03] text-white/70 transition hover:bg-white/[0.07] hover:text-white"
                aria-label="Notifications"
              >
                <svg
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.8"
                >
                  <path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9" />

                  <path d="M13.73 21a2 2 0 0 1-3.46 0" />
                </svg>

                {unreadCount > 0 && (
                  <span className="absolute -right-1 -top-1 flex min-w-5 items-center justify-center rounded-full bg-cyan-400 px-1.5 py-0.5 text-[10px] font-bold text-black">
                    {unreadCount > 99 ? "99+" : unreadCount}
                  </span>
                )}
              </button>

              {/* Notification dropdown */}

              {notificationOpen && (
                <NotificationDropdown
                  notifications={notifications}
                  onNotificationClick={handleNotificationClick}
                  onMarkAllRead={handleMarkAllRead}
                />
              )}
            </div>

            <button
              type="button"
              onClick={() => {
                clearHospitalAuth();

                router.replace("/hospital/login");
              }}
              className="rounded-xl border border-white/10 px-4 py-2 text-sm text-white/70 transition hover:bg-white/5 hover:text-white"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* DASHBOARD */}

      <section className="mx-auto max-w-7xl px-8 py-10">
        <h2 className="text-3xl font-semibold">Dashboard</h2>

        <p className="mt-2 text-white/50">
          Manage your hospital appointments and requests.
        </p>

        <div className="mt-8 grid gap-5 md:grid-cols-3">
          <DashboardCard title="Pending Requests" value="—" />

          <DashboardCard title="Today's Appointments" value="—" />

          <DashboardCard title="Total Appointments" value="—" />
        </div>

        <div className="mt-8 rounded-2xl border border-white/10 bg-white/[0.03] p-6">
          <h3 className="text-lg font-semibold">Appointment Requests</h3>

          <p className="mt-2 text-sm text-white/40">
            Appointment requests will appear here.
          </p>
        </div>
      </section>
    </main>
  );
}

function DashboardCard({ title, value }: { title: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-6">
      <div className="text-sm text-white/50">{title}</div>

      <div className="mt-3 text-3xl font-semibold">{value}</div>
    </div>
  );
}

function NotificationDropdown({
  notifications,
  onNotificationClick,
  onMarkAllRead,
}: {
  notifications: HospitalNotification[] | null;

  onNotificationClick: (notification: HospitalNotification) => void;

  onMarkAllRead: () => void;
}) {
  return (
    <div className="absolute right-0 top-14 z-50 w-[380px] overflow-hidden rounded-2xl border border-white/10 bg-[#0b1320] shadow-2xl shadow-black/50">
      {/* Header */}

      <div className="flex items-center justify-between border-b border-white/[0.07] px-4 py-4">
        <div>
          <h3 className="font-semibold text-white">Notifications</h3>

          <p className="mt-0.5 text-xs text-white/35">Appointment updates</p>
        </div>

        {notifications !== null &&
          notifications.some((notification) => !notification.is_read) && (
            <button
              type="button"
              onClick={onMarkAllRead}
              className="text-xs text-cyan-400 transition hover:text-cyan-300"
            >
              Mark all read
            </button>
          )}
      </div>

      {/* Content */}

      <div className="max-h-[480px] overflow-y-auto">
        {/* Loading */}

        {notifications === null && (
          <div className="px-5 py-8 text-center text-sm text-white/40">
            Loading notifications...
          </div>
        )}

        {/* Empty */}

        {notifications !== null && notifications.length === 0 && (
          <div className="px-5 py-10 text-center">
            <div className="text-2xl">✓</div>

            <div className="mt-2 text-sm text-white/60">
              You re all caught up.
            </div>

            <div className="mt-1 text-xs text-white/30">
              No new notifications.
            </div>
          </div>
        )}

        {/* Notifications */}

        {notifications !== null &&
          notifications.map((notification) => (
            <button
              type="button"
              key={notification.id}
              onClick={() => onNotificationClick(notification)}
              className={`w-full border-b border-white/[0.05] px-4 py-4 text-left transition hover:bg-white/[0.05] ${
                notification.is_read ? "bg-transparent" : "bg-cyan-400/[0.05]"
              }`}
            >
              <div className="flex gap-3">
                <div className="pt-1">
                  <span
                    className={`block h-2.5 w-2.5 rounded-full ${
                      notification.is_read ? "bg-white/20" : "bg-cyan-400"
                    }`}
                  />
                </div>

                <div className="min-w-0 flex-1">
                  <div className="flex items-start justify-between gap-3">
                    <div className="text-sm font-medium text-white">
                      {notification.title}
                    </div>

                    {!notification.is_read && (
                      <span className="shrink-0 text-[10px] font-medium uppercase tracking-wider text-cyan-400">
                        New
                      </span>
                    )}
                  </div>

                  <p className="mt-1 text-sm leading-5 text-white/50">
                    {notification.message}
                  </p>

                  <div className="mt-2 text-xs text-white/25">
                    {formatNotificationTime(notification.created_at)}
                  </div>
                </div>
              </div>
            </button>
          ))}
      </div>
    </div>
  );
}

function formatNotificationTime(value: string) {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "";
  }

  return date.toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}
