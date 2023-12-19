#ifndef __avswitch_h
#define __avswitch_h

#include <lib/base/object.h>
#include <lib/python/connections.h>

class eSocketNotifier;

class eAVSwitch: public sigc::trackable
{
	static eAVSwitch *instance;
	int m_video_mode;
	bool m_active;
	ePtr<eSocketNotifier> m_fp_notifier;
	void fp_event(int what);
	int m_fp_fd;
#ifdef SWIG
	eAVSwitch();
	~eAVSwitch();
#endif
protected:
public:
#ifndef SWIG
	eAVSwitch();
	~eAVSwitch();
#endif
	static eAVSwitch *getInstance();
	bool haveScartSwitch();
	int getVCRSlowBlanking();
	void setColorFormat(int format);
	void setAspectRatio(int ratio);
	void setInput(int val);
	void setWSS(int val);
	void setVideoMode(const std::string &newMode, int flags = 0) const;
	bool isActive();
	
	enum
	{
		FLAGS_DEBUG = 1,
		FLAGS_SUPPRESS_NOT_EXISTS = 2,
		FLAGS_SUPPRESS_READWRITE_ERROR = 4
	};
	
	PSignal1<void, int> vcr_sb_notifier;
};

#endif
