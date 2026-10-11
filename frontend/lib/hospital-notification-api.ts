import { hospitalRequest } from "@/lib/hospital-api";

export type HospitalNotification = {
  id: number;
  hospital_id: number;
  appointment_request_id: number | null;

  type: string;
  title: string;
  message: string;

  is_read: boolean;

  created_at: string;
  read_at: string | null;
};

type NotificationsResponse = {
  success: boolean;
  data: HospitalNotification[];
};

type UnreadCountResponse = {
  success: boolean;
  unread_count: number;
};

type NotificationActionResponse = {
  success: boolean;
  message: string;
  data?: unknown;
};

export async function getHospitalNotifications() {
  return hospitalRequest<NotificationsResponse>(
    "/ai/hospital/notifications"
  );
}

export async function getHospitalUnreadCount() {
  return hospitalRequest<UnreadCountResponse>(
    "/ai/hospital/notifications/unread-count"
  );
}

export async function markNotificationAsRead(
  notificationId: number
) {
  return hospitalRequest<NotificationActionResponse>(
    `/ai/hospital/notifications/${notificationId}/read`,
    {
      method: "POST",
    }
  );
}

export async function markAllNotificationsAsRead() {
  return hospitalRequest<NotificationActionResponse>(
    "/ai/hospital/notifications/read-all",
    {
      method: "POST",
    }
  );
}