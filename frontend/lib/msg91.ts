export function initializeMsg91() {
  if (typeof window === "undefined") {
    throw new Error(
      "MSG91 can only be initialized in the browser."
    );
  }

  if (!window.initSendOTP) {
    throw new Error(
      "MSG91 SDK has not loaded yet."
    );
  }

  const widgetId =
    process.env.NEXT_PUBLIC_MSG91_WIDGET_ID;

  const tokenAuth =
    process.env.NEXT_PUBLIC_MSG91_AUTH_TOKEN;

  if (!widgetId) {
    throw new Error(
      "NEXT_PUBLIC_MSG91_WIDGET_ID is missing."
    );
  }

  if (!tokenAuth) {
    throw new Error(
      "NEXT_PUBLIC_MSG91_AUTH_TOKEN is missing."
    );
  }

  window.initSendOTP({
    widgetId,
    tokenAuth,
    exposeMethods: true,

    // MSG91 requires these callbacks
    success: (data: Msg91CallbackData) => {
      console.log(
        "MSG91 verification event:",
        data
      );
    },

    failure: (error: unknown) => {
      console.error(
        "MSG91 verification event:",
        error
      );
    },
  });
}


export function getMsg91ErrorMessage(
  error: unknown,
  fallback: string
): string {
  if (!error) {
    return fallback;
  }

  if (typeof error === "string") {
    return error;
  }

  if (
    typeof error === "object" &&
    error !== null
  ) {
    const errorObject =
      error as Record<string, unknown>;

    const message =
      errorObject.message ??
      errorObject.msg ??
      errorObject.description ??
      errorObject.error;

    if (typeof message === "string") {
      return message;
    }
  }

  return fallback;
}