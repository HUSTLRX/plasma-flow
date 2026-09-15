#pragma once
#include <cstdint>

// An inactive oneshot is also its pre-start state. Require successful completion
// in THIS KSMServer session, not a stale completion from an earlier login.
inline bool restorationReady(bool sessionActive, bool restoreInactive, bool success,
                             int exitStatus, uint64_t sessionStarted, uint64_t restoreFinished)
{
    return sessionActive && restoreInactive && success && exitStatus == 0
        && sessionStarted > 0 && restoreFinished >= sessionStarted;
}
